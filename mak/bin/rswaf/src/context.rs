use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs;
use std::mem::swap;
use std::ops::Deref;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use blake3::Hasher;
use mlua::prelude::{LuaError, LuaFunction, LuaResult, LuaString, LuaTable, LuaValue};
use mlua::{AnyUserData, FromLua, IntoLua, Lua, MetaMethod, Table, UserData, UserDataFields, UserDataMethods};
use crate::command::{Command, CommandSpec, CommandHash, CommandOutput, CommandStatus, GroupStatus};
use crate::environment::ReadWriteEnvironment;
use crate::error::Result;
use crate::generator::Generator;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use crate::subprocess::Popen;

pub(crate) struct Context {
    spec: CommandSpec,
    pub(crate) output: CommandOutput,
    environment: Arc<Mutex<ReadWriteEnvironment>>,
    path: Node,
    src_dir: Node,
    bld_dir: Node,
    options: Options,
    logger: Logger,
    command_path: Vec<String>,
    commands: HashMap<String, Vec<String>>,
    sorted_features: Vec<String>,
    partial_order: Vec<(String, String)>,
    in_post: usize,
}

struct DeclaredCommand {
    path: Vec<usize>,
}

struct Feature(String, Vec<String>);

const ROOT_SCRIPT: &str = "make.lua";

impl Context {
    pub(crate) fn new(
        spec: CommandSpec,
        options_context: Options,
        envs: &Vec<Arc<Mutex<ReadWriteEnvironment>>>,
        tools: &Vec<Node>,
        command_path: Vec<String>,
    ) -> Result<Context> {
        let current_dir = Node::from(&std::env::current_dir()?);
        let bld_dir = if let Options::Environment(options) = &options_context {
            options.get_raw("out").as_node(&current_dir)?
        } else {
            current_dir.clone()
        };
        bld_dir.mkdir()?;
        let run_envs: Vec<Arc<Mutex<ReadWriteEnvironment>>> = spec
            .envs
            .iter()
            .enumerate()
            .map(|(i, &x)| Arc::new(Mutex::new(ReadWriteEnvironment::derive_from_parent(&envs[x], i))))
            .collect();
        let start_env = run_envs[0].clone();
        Ok(Context {
            spec: spec.clone(),
            output: CommandOutput {
                environments: run_envs,
                options: match &options_context {
                    Options::CommandLineParser(_) => None,
                    Options::Environment(e) => Some(e.clone()),
                },
                commands: Vec::new(),
                tools: tools.clone(),
                stored_hash: CommandHash {
                    file_dependencies: Vec::new(),
                    option_dependencies: Vec::new(),
                    variable_dependencies: Vec::new(),
                    glob_dependencies: Vec::new(),
                    hash: None,
                },
                groups: vec![(spec.name.clone(), GroupStatus::Enabled)],
            },
            environment: start_env,
            path: current_dir.clone(),
            src_dir: current_dir,
            bld_dir,
            options: options_context,
            logger: Logger::new(None, 0, false),
            command_path,
            commands: HashMap::new(),
            sorted_features: Vec::new(),
            partial_order: Vec::new(),
            in_post: 0,
        })
    }

    pub(crate) fn run(
        &mut self,
        envs: &Vec<Arc<Mutex<ReadWriteEnvironment>>>,
        tools: &Vec<Node>,
        commands: &mut HashMap<String, Vec<String>>,
        mut logger: Logger,
    ) -> Result<Logger> {
        swap(commands, &mut self.commands);
        swap(&mut logger, &mut self.logger);

        {
            let lua = Lua::new();
            let globals = lua.globals();

            let run = |userdata: &mut AnyUserData, path| -> LuaResult<()> {
                let chunk = lua.load(path);
                {
                    chunk.call(userdata.clone())
                }
            };

            lua.scope(|scope| {
                let mut userdata = scope.create_userdata_ref_mut(self).unwrap();
                userdata.set_named_user_value(":features", lua.create_table()?)?;
                userdata.set_named_user_value(":generators", lua.create_table()?)?;
                for path in tools {
                    run(&mut userdata, path.abs_path())?;
                }

                run(&mut userdata, Path::new(ROOT_SCRIPT))?;

                {
                    let mut context = userdata.borrow_mut::<Context>()?;
                    context.in_post = 1;
                }
                for generator in userdata.named_user_value::<Vec<AnyUserData>>(":generators")? {
                    post(&lua, (&userdata, &generator))?;
                }

                Ok(())
            })?;

            /* retrieve a list of modules */
            let package: Table = globals.get("package")?;
            let package_path: String = package.get("path")?;
            let packages: Table = package.get("loaded")?;
            packages.for_each(|key: String, _: LuaValue| {
                for path in package_path.split(';') {
                    let module_path = path.replace("?", key.replace(".", "/").as_str());

                    if Path::new(module_path.as_str()).is_file() {
                        self.output
                            .stored_hash
                            .file_dependencies
                            .push(PathBuf::from(module_path));
                        break;
                    }
                }
                Ok(())
            })?;
        }
        for env in envs {
            self.output.stored_hash.variable_dependencies.push(
                env.lock()
                    .unwrap()
                    .environment
                    .used_keys
                    .iter()
                    .map(|x| x.clone())
                    .collect(),
            )
        }
        if let Some(options_env) = &self.output.options {
            self.output.stored_hash.option_dependencies = options_env
                .used_keys
                .iter()
                .map(|x| x.clone())
                .collect();
        }
        self.output.stored_hash.hash = Some(self.output.hash(self.output.options.as_ref(), envs, &self.output.tools)?);
        swap(commands, &mut self.commands);
        swap(&mut logger, &mut self.logger);

        Ok(logger)
    }

    fn declare_command(
        self: &mut Context,
        name: &str,
        function: &str,
        envs: Vec<usize>,
    ) -> LuaResult<Vec<usize>> {
        match self.commands.entry(name.to_string()) {
            Entry::Occupied(e) => Err(LuaError::RuntimeError(format!(
                "command '{}' already declared with full path: '{}'",
                name,
                e.get().join("::")
            ))),
            Entry::Vacant(v) => {
                let mut full_path = self.command_path.clone();
                let spec = CommandSpec {
                    name: name.to_string(),
                    function: function.to_string(),
                    envs,
                };
                self.output.commands.push(Command {
                    spec,
                    output: None,
                    status: CommandStatus::Defined,
                });
                full_path.push(name.to_string());
                v.insert(full_path);
                Ok(vec![self.output.commands.len() - 1])
            }
        }
    }

    fn declare_chain(
        self: &mut Context,
        path: &DeclaredCommand,
        name: &str,
        function: &str,
    ) -> LuaResult<Vec<usize>> {
        match self.commands.entry(name.to_string()) {
            Entry::Occupied(e) => Err(LuaError::RuntimeError(format!(
                "command '{}' already declared with full path: '{}'",
                name,
                e.get().join("::")
            ))),
            Entry::Vacant(v) => {
                let mut full_path = self.command_path.clone();
                let mut cmd = &mut self.output.commands[path.path[0]];
                full_path.push(cmd.spec.name.clone());
                for &index in (&path.path).into_iter().skip(1) {
                    cmd = &mut cmd.output.as_mut().unwrap().commands[index];
                    full_path.push(cmd.spec.name.clone());
                }
                let spec = CommandSpec {
                    name: name.to_string(),
                    function: function.to_string(),
                    envs: Vec::new(),
                };
                if cmd.output.is_none() {
                    cmd.output = Some(CommandOutput {
                        environments: Vec::new(),
                        commands: Vec::new(),
                        options: None,
                        tools: Vec::new(),
                        stored_hash: CommandHash {
                            file_dependencies: Vec::new(),
                            option_dependencies: Vec::new(),
                            variable_dependencies: Vec::new(),
                            glob_dependencies: Vec::new(),
                            hash: None,
                        },
                        groups: Vec::new(),
                    });
                }
                cmd.output.as_mut().unwrap().commands.push(Command {
                    spec,
                    output: None,
                    status: CommandStatus::ForwardDeclared,
                });
                full_path.push(name.to_string());
                v.insert(full_path);
                Ok(vec![self.output.commands.len()])
            }
        }
    }
}


fn partial_sort(mut features: Vec<String>, partial_order: &Vec<(String, String)>) -> LuaResult<Vec<String>> {
    for edge in partial_order {
        if let None = features.iter().position(|x| x.eq(&edge.0)) {
            return Err(LuaError::RuntimeError(format!("Dependency on unknown feature {}", &edge.0)));
        }
        if let None = features.iter().position(|x| x.eq(&edge.1)) {
            return Err(LuaError::RuntimeError(format!("Dependency on unknown feature {}", &edge.1)));
        }
    }

    let mut result = Vec::new();
    let mut edges = partial_order.clone();

    let mut roots = Vec::new();

    while let Some(index) = features.iter().position(|x| !edges.iter().any(|edge| edge.1.eq(x))) {
        roots.push(features.remove(index));
    }
    roots.reverse();

    while !roots.is_empty() {
        let root = roots.pop().unwrap();
        while let Some(edge_index) = edges.iter().position(|x| x.0.eq(&root)) {
            let edge = edges.swap_remove(edge_index);
            if !edges.iter().any(|e| e.1.eq(&edge.1)) {
                if let Some(new_root) = features.iter().position(|x| x.eq(&edge.1)) {
                    roots.insert(0, features.swap_remove(new_root));
                }
            }
        }
        result.push(root);
    }

    if !edges.is_empty() {
        Err(LuaError::RuntimeError(format!("Cycle detected in feature dependency:\n  {}",
                                           edges.iter().map(|x| format!("{} -> {}", x.0, x.1)).collect::<Vec<_>>().join("\n  "))))
    } else {
        Ok(result)
    }
}

fn post(_lua: &Lua, (this, generator): (&AnyUserData, &AnyUserData)) -> LuaResult<()> {
    let (generator_name, features) =
        {
            let mut result_features = Vec::new();

            let owner = this.borrow::<Context>()?;
            let generator_arc = generator.borrow_mut::<Arc<Mutex<Generator>>>()?;
            let mut generator = generator_arc.lock().unwrap();
            if generator.posted {
                return Ok(());
            }
            generator.posted = true;
            if owner.in_post == 0 {
                return Err(LuaError::RuntimeError(format!("Posting task generator {} outside of post", &generator.name)));
            }
            let mut available_features = Vec::new();
            for u in this.named_user_value::<Vec<AnyUserData>>(":features")? {
                let f = u.borrow::<Feature>()?;
                available_features.push((f.0.clone(), f.1.clone(), u.named_user_value::<LuaFunction>(":call")?));
            }
            for feature_name in &owner.sorted_features {
                let feature = available_features.iter().find(|x| x.0.eq(feature_name)).unwrap();
                for f in &generator.features {
                    if let Some(_) = feature.1.iter().position(|x| x.eq(f)) {
                        result_features.push(feature.clone());
                        break;
                    }
                }
            }
            (generator.name.clone(), result_features)
        };

    for (name, _, callback) in features {
        {
            let mut owner = this.borrow_mut::<Context>()?;
            let depth = owner.in_post - 1;
            owner.logger.debug(format!("{}posting {}:{}", " ".repeat(depth), generator_name, name).as_str());
            owner.in_post += 1;
        }
        let result = callback.call(generator);
        {
            let mut owner = this.borrow_mut::<Context>()?;
            owner.in_post -= 1;
        }
        if result.is_err() { return result; }
    }

    Ok(())
}

impl UserData for Feature {}

impl UserData for DeclaredCommand {}

impl UserData for Context {
    fn add_fields<'lua, F: UserDataFields<'lua, Self>>(fields: &mut F) {
        fields.add_field_method_get("name", |_, this| Ok(this.spec.name.clone()));
        fields.add_field_method_get("fun", |_, this| Ok(this.spec.function.clone()));
        fields.add_field_method_get("env", |_, this| Ok(this.environment.clone()));
        fields.add_field_method_get("path", |_, this| Ok(this.path.clone()));
        fields.add_field_method_get("src_dir", |_, this| Ok(this.src_dir.clone()));
        fields.add_field_method_get("bld_dir", |_, this| Ok(this.bld_dir.clone()));
        fields.add_field_method_get("settings", |lua, this| match &this.options {
            Options::CommandLineParser(context) => context.clone().into_lua(lua),
            Options::Environment(env) => env.clone().into_lua(lua),
        });
    }

    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_function_mut(MetaMethod::NewIndex, |_lua, (context, name, value): (AnyUserData, String, LuaValue)| {
            context.set_named_user_value(name.as_str(), value)
        });

        methods.add_meta_function_mut(MetaMethod::Index, |_lua, (context, name): (AnyUserData, String)| {
            let result = context.named_user_value::<LuaValue<'lua>>(name.as_str())?;
            if result.is_nil() {
                Err(LuaError::RuntimeError(format!("Context does not have a user value `{}`", name)))
            } else { Ok(result) }
        });

        methods.add_function("recurse", |lua, args: (AnyUserData, LuaString)| {
            let (old_path, script) = {
                let mut this = args.0.borrow_mut::<Context>()?;
                let mut script = this.path.make_node(&PathBuf::from(args.1.to_str()?));
                if script.is_dir() {
                    let mut script_path = PathBuf::from(&this.spec.function);
                    script_path.set_extension("lua");
                    script = script.make_node(&script_path);
                }
                let mut old_path = script.parent();
                swap(&mut old_path, &mut this.path);
                this.output
                    .stored_hash
                    .file_dependencies
                    .push(script.path().clone());
                (old_path, script)
            };
            let result: LuaResult<()> = lua.load(script.abs_path()).call(&args.0);
            {
                let mut this = args.0.borrow_mut::<Context>()?;
                this.path = old_path;
            }
            result
        });

        methods.add_method_mut(
            "declare_command",
            |lua, this: &mut Context, args: (String, String, LuaValue)| {
                let mut envs = Vec::new();
                if args.2.is_table() {
                    for env in Vec::<AnyUserData>::from_lua(args.2, lua)? {
                        envs.push(
                            env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?
                                .lock()
                                .unwrap()
                                .index,
                        );
                    }
                } else {
                    let env = args
                        .2
                        .as_userdata()
                        .unwrap()
                        .borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?;
                    envs.push(env.lock().unwrap().index);
                }
                let path = this.declare_command(args.0.as_str(), args.1.as_str(), envs)?;
                Ok(DeclaredCommand { path })
            },
        );

        methods.add_method_mut(
            "chain_command",
            |_lua, this: &mut Context, args: (AnyUserData, String, String)| {
                let path = args.0.borrow_mut::<DeclaredCommand>()?;
                let sub_path =
                    this.declare_chain(path.deref(), args.1.as_str(), args.2.as_str())?;
                Ok(DeclaredCommand { path: sub_path })
            },
        );

        methods.add_method_mut("derive", |_lua, this: &mut Context, env: AnyUserData| {
            let env_ref = env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?;
            let new_env = Arc::new(Mutex::new(ReadWriteEnvironment::derive(
                &env_ref.clone(),
                this.output.environments.len(),
            )));
            this.output.environments.push(new_env.clone());
            Ok(new_env)
        });

        methods.add_method_mut("debug", |_lua, this, message: String| {
            this.logger.debug(message.as_str());
            Ok(())
        });

        methods.add_method_mut("info", |_lua, this, message: String| {
            this.logger.info(message.as_str());
            Ok(())
        });

        methods.add_method_mut("warn", |_lua, this, message: String| {
            this.logger.warning(message.as_str());
            Ok(())
        });

        methods.add_method_mut("error", |_lua, this, message: String| {
            this.logger.error(message.as_str());
            Ok(())
        });

        methods.add_method_mut("fatal", |_lua, _this, message: String| -> LuaResult<()> {
            Err(LuaError::RuntimeError(message))
        });

        methods.add_method_mut("set_status", |_lua, this, message: String| {
            this.logger.set_status(message.as_str());
            Ok(())
        });

        methods.add_method_mut("clear_status", |_lua, this, ()| {
            this.logger.clear_status();
            Ok(())
        });

        methods.add_function_mut(
            "with",
            |_lua, (context, env, function): (AnyUserData, AnyUserData, LuaFunction)| {
                let prev_env = {
                    let mut context = context.borrow_mut::<Context>()?;
                    let env = env.borrow_mut::<Arc<Mutex<ReadWriteEnvironment>>>()?;
                    let prev_env = context.environment.clone();
                    context.environment = env.clone();
                    drop(env);
                    prev_env
                };
                let result: LuaResult<LuaValue> = function.call(());
                let mut context = context.borrow_mut::<Context>()?;
                context.environment = prev_env;
                result
            },
        );

        methods.add_function(
            "try",
            |_lua, args: (AnyUserData, String, LuaFunction)| -> LuaResult<()> {
                {
                    let mut this = args.0.borrow_mut::<Context>()?;
                    this.logger.begin(args.1.as_str());
                }
                let result: LuaResult<LuaValue> = args.2.call(());
                {
                    let mut this = args.0.borrow_mut::<Context>()?;
                    match result {
                        Ok(v) => {
                            if v.is_nil() {
                                Ok(this.logger.end("Ok", true))
                            } else {
                                Ok(this.logger.end(v.to_string().unwrap().as_str(), true))
                            }
                        }
                        Err(e) => match &e {
                            LuaError::RuntimeError(s) => Ok(this.logger.end(s.as_str(), false)),
                            LuaError::CallbackError {
                                traceback: _,
                                cause,
                            } => match cause.as_ref() {
                                LuaError::RuntimeError(s) => Ok(this.logger.end(s.as_str(), false)),
                                _ => Ok(this.logger.end(e.to_string().as_str(), false)),
                            },
                            _ => Ok(this.logger.end(e.to_string().as_str(), false)),
                        },
                    }
                }
            },
        );

        methods.add_method_mut(
            "search",
            |_lua, this, (path, pattern): (Node, String)| {
                let mut result = Vec::new();
                if path.is_dir() {
                    let path = Node::from(&fs::canonicalize(path.path()).unwrap());
                    let paths = glob::glob(
                        &path.path()
                            .join(&pattern)
                            .to_string_lossy()
                            .deref()
                    ).map_err(|e| LuaError::RuntimeError(format!("pattern error: {}", e)))?;
                    let mut hasher = Hasher::new();
                    for path in paths {
                        if let Ok(path) = path {
                            hasher.update(path.as_os_str().as_encoded_bytes());
                            result.push(Node::from(&path));
                        }
                    }
                    let mut store = true;
                    let hash = hasher.finalize();
                    for (prev_path, prev_pattern, prev_hash) in &this.output.stored_hash.glob_dependencies {
                        if prev_path.path().eq(path.path()) & &prev_pattern.eq(&pattern) {
                            if !hash.eq(&prev_hash.0) {}
                            store = false;
                        }
                    }
                    if store {
                        this.output.stored_hash.glob_dependencies.push((path.clone(), pattern, crate::command::SerializedHash(hash)));
                    }
                }
                Ok(result)
            },
        );

        methods.add_method(
            "popen",
            |_lua, _this, command: Vec<LuaValue>| {
                let mut cmd = Vec::new();
                for x in command {
                    cmd.push(x.to_string()?);
                }
                Popen::create(&cmd)
            },
        );

        methods.add_function(
            "load_tool",
            |lua, (this, tool, again): (AnyUserData, String, Option<bool>)| {
                let paths = {
                    let mut nodes = Vec::new();
                    let mut this = this.borrow_mut::<Context>()?;
                    for x in match &mut this.options {
                        Options::Environment(e) => e.get_into_list("tools_dir"),
                        Options::CommandLineParser(cl) => {
                            let cl = cl.lock().unwrap();
                            cl.get_value("tools_dir")?.into_list()
                        }
                    } {
                        nodes.push(x.as_node(&this.path)?);
                    }
                    nodes
                };

                for node in &paths {
                    let node = node.make_node(&PathBuf::from(tool.to_owned() + ".lua"));
                    if node.is_file() {
                        let do_run =
                            {
                                let mut this = this.borrow_mut::<Context>()?;
                                if let None = this.output.tools.iter().find(|&x| x == &node) {
                                    this.output.tools.push(node.clone());
                                    true
                                } else {
                                    again.is_some() && again.unwrap()
                                }
                            };

                        if do_run {
                            lua.load(node.abs_path()).call(this)?;
                        }
                        return Ok(());
                    }
                }


                let this = this.borrow::<Context>()?;
                Err(LuaError::RuntimeError(
                    format!("could not locate tool {}\nsearch paths:\n  {}\ncurrent directory:\n  {}\n",
                            tool,
                            paths.iter().map(|x| x.to_string()).collect::<Vec<String>>().join(",\n  "),
                            this.path
                    )))
            },
        );

        methods.add_meta_function(
            MetaMethod::Call,
            |lua, (this, name, features, group): (AnyUserData, String, LuaValue, Option<String>)| {
                if let Some(group) = &group {
                    let context = this.borrow::<Context>()?;
                    if let None = context.output.groups.iter().position(|x| x.0.eq(&name)) {
                        return Err(LuaError::RuntimeError(format!("When creating generator `{}`: `{}`: group was not declared", &name, group)));
                    }
                }
                let features = match &features {
                    LuaValue::String(s) => s.to_string_lossy().to_string().split(',').map(|x| x.trim().to_string()).collect(),
                    LuaValue::Table(_) => { Vec::<String>::from_lua(features, lua)? }
                    LuaValue::Nil => Vec::new(),
                    _ => return Err(LuaError::RuntimeError("features should be a list of string or a single string".to_string())),
                };

                let generator = {
                    let this = this.borrow::<Context>()?;
                    let group = match group {
                        Some(x) => x,
                        None => this.spec.function.clone(),
                    };
                    lua.create_userdata(Arc::new(Mutex::new(Generator::new(name, group, features))))?
                };

                this.named_user_value::<LuaTable>(":generators")?.push(generator.clone())?;
                Ok(generator)
            },
        );

        methods.add_function(
            "feature",
            |lua, (this, feature_names, name, method, after, before): (AnyUserData, LuaValue, String, LuaFunction, Option<Vec<String>>, Option<Vec<String>>)| {
                let feature_names = match &feature_names {
                    LuaValue::String(s) => s.to_string_lossy().to_string().split(',').map(|x| x.trim().to_string()).collect(),
                    LuaValue::Table(_) => { Vec::<String>::from_lua(feature_names, lua)? }
                    LuaValue::Nil => Vec::new(),
                    _ => return Err(LuaError::RuntimeError("features should be a list of string or a single string".to_string())),
                };

                let mut features = this.named_user_value::<Vec<AnyUserData>>(":features")?;
                {
                    let mut ordered_features = Vec::new();
                    for f in features.iter() {
                        let feature_name = f.borrow::<Feature>()?.0.clone();
                        if feature_name.eq(&name) {
                            return Err(LuaError::RuntimeError(format!("Feature {} already defined.", name)));
                        }
                        ordered_features.push(feature_name);
                    }
                    ordered_features.push(name.clone());
                    let mut this = this.borrow_mut::<Context>()?;
                    let mut partial_order = this.partial_order.clone();
                    for before in before.or_else(|| Some(Vec::new())).unwrap() {
                        partial_order.push((name.clone(), before));
                    }
                    for after in after.or_else(|| Some(Vec::new())).unwrap() {
                        partial_order.push((after, name.clone()));
                    }

                    /* verify on the dummy data that all features exist and that there is no cycle */
                    this.sorted_features = partial_sort(ordered_features, &partial_order)?;
                    this.partial_order = partial_order;
                };

                let feature = lua.create_any_userdata(Feature(name, feature_names))?;
                feature.set_named_user_value(":call", method)?;
                features.push(feature);
                this.set_named_user_value(":features", features)?;

                Ok(())
            },
        );

        methods.add_function("post", |lua, (this, generator): (AnyUserData, AnyUserData)| post(lua, (&this, &generator)));

        methods.add_method_mut(
            "declare_group",
            |_lua, this, (name, enabled): (String, LuaValue)| {
                if let Some(_) = this.output.groups.iter().position(|x| x.0.eq(&name)) {
                    Err(LuaError::RuntimeError(format!("`{}`: build group already registered", &name)))
                } else {
                    let status = match enabled {
                        LuaValue::Nil => GroupStatus::Enabled,
                        LuaValue::Integer(i) => if i == 0 { GroupStatus::Disabled } else { GroupStatus::Enabled },
                        LuaValue::Boolean(b) => if b { GroupStatus::Enabled } else { GroupStatus::Disabled },
                        LuaValue::String(s) => GroupStatus::Conditional(s.to_string_lossy().to_string()),
                        _ => return Err(LuaError::RuntimeError("Parameter `enabled` of method `declare_group` should be nil, a boolean, or a string".to_string())),
                    };
                    this.output.groups.push((name.clone(), status));
                    Ok(())
                }
            },
        )
    }
}
