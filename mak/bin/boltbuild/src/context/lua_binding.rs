use super::{Context, TOOLS_DIR};
use super::operations::{DeclaredCommand, Feature, post};
use super::subprocess::Process;

use std::fs;
use std::ops::Deref;
use std::mem::swap;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use blake3::Hasher;
use mlua::{FromLua, IntoLua, AnyUserData, MetaMethod, UserData, UserDataFields, UserDataMethods};
use mlua::prelude::{LuaError, LuaFunction, LuaResult, LuaString, LuaTable, LuaValue};
use crate::command::{GroupStatus, SerializedHash};
use crate::driver::Driver;
use crate::environment::ReadWriteEnvironment;
use crate::generator::Generator;
use crate::node::Node;
use crate::options::Options;

fn partial_sort(mut features: Vec<String>, partial_order: &Vec<(String, String)>) -> LuaResult<Vec<String>> {
    for edge in partial_order {
        if !features.iter().any(|x| x.eq(&edge.0)) {
            return Err(LuaError::RuntimeError(format!("Dependency on unknown feature {}", &edge.0)));
        }
        if !features.iter().any(|x| x.eq(&edge.1)) {
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

    while let Some(root) = roots.pop() {
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

struct FeatureIndex(usize);

impl UserData for FeatureIndex {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_function("set_run_after", |_lua, (this, predecessors): (AnyUserData, Vec<String>)| {
            let context = this.user_value::<AnyUserData>()?;
            let feature_index = this.borrow::<FeatureIndex>()?.0;
            let features = context.named_user_value::<Vec<AnyUserData>>(":features")?;
            {
                let mut ordered_features = Vec::new();
                for f in features.iter() {
                    let feature_name = f.borrow::<Feature>()?.0.clone();
                    ordered_features.push(feature_name);
                }
                let name = &ordered_features[feature_index];
                let mut context = context.borrow_mut::<Context>()?;
                let mut partial_order = context.partial_order.clone();
                for predecessor in predecessors {
                    partial_order.push((predecessor, name.clone()));
                }

                /* verify on the dummy data that all features exist and that there is no cycle */
                context.sorted_features = partial_sort(ordered_features, &partial_order)?;
                context.partial_order = partial_order;
            };
            Ok(this)
        });
        methods.add_function("set_run_before", |_lua, (this, successors): (AnyUserData, Vec<String>)| {
            let context = this.user_value::<AnyUserData>()?;
            let feature_index = this.borrow::<FeatureIndex>()?.0;
            let features = context.named_user_value::<Vec<AnyUserData>>(":features")?;
            {
                let mut ordered_features = Vec::new();
                for f in features.iter() {
                    let feature_name = f.borrow::<Feature>()?.0.clone();
                    ordered_features.push(feature_name);
                }
                let name = &ordered_features[feature_index];
                let mut context = context.borrow_mut::<Context>()?;
                let mut partial_order = context.partial_order.clone();
                for successor in successors {
                    partial_order.push((name.clone(), successor));
                }

                /* verify on the dummy data that all features exist and that there is no cycle */
                context.sorted_features = partial_sort(ordered_features, &partial_order)?;
                context.partial_order = partial_order;
            };
            Ok(this)
        });
    }
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

        methods.add_method_mut("derive", |_lua, this: &mut Context, env: Option<AnyUserData>| {
            let from_env = if let Some(env) = env {
                env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?.deref().clone()
            } else {
                this.environment.clone()
            };
            let new_env = Arc::new(Mutex::new(ReadWriteEnvironment::derive(
                &from_env,
                this.output.environments.len(),
            )?));
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

        methods.add_method_mut("print", |_lua, this, message: String| -> LuaResult<()> {
            this.logger.print(message.as_str());
            Ok(())
        });

        methods.add_method_mut("colored_print", |_lua, this, message: String| -> LuaResult<()> {
            this.logger.colored_print(message.as_str());
            Ok(())
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
                                this.logger.end("Ok", true);
                                Ok(())
                            } else {
                                this.logger.end(v.to_string().unwrap().as_str(), true);
                                Ok(())
                            }
                        }
                        Err(e) => match &e {
                            LuaError::RuntimeError(s) => {
                                this.logger.end(s.as_str(), false);
                                Ok(())
                            }
                            LuaError::CallbackError {
                                traceback: _,
                                cause,
                            } => match cause.as_ref() {
                                LuaError::RuntimeError(s) => {
                                    this.logger.end(s.as_str(), false);
                                    Ok(())
                                }
                                _ => {
                                    this.logger.end(e.to_string().as_str(), false);
                                    Ok(())
                                }
                            },
                            _ => {
                                this.logger.end(e.to_string().as_str(), false);
                                Ok(())
                            }
                        },
                    }
                }
            },
        );

        methods.add_method_mut(
            "search",
            |_lua, this, (path, pattern, include_directories): (Node, String, Option<bool>)| {
                let mut result = Vec::new();
                if path.is_dir() {
                    let include_directories = include_directories.unwrap_or(false);
                    let path = Node::from(&fs::canonicalize(path.path()).unwrap());
                    let paths = glob::glob(
                        path.path()
                            .join(&pattern)
                            .to_string_lossy()
                            .deref()
                    ).map_err(|e| LuaError::RuntimeError(format!("pattern error: {}", e)))?;
                    let mut hasher = Hasher::new();
                    for path in paths.flatten() {
                        hasher.update(path.as_os_str().as_encoded_bytes());
                        if include_directories || !path.is_dir() {
                            result.push(Node::from(&path));
                        }
                    }
                    let mut store = true;
                    let hash = hasher.finalize();
                    for (prev_path, prev_pattern, prev_hash) in &this.output.stored_hash.glob_dependencies {
                        if prev_path.path().eq(path.path()) & prev_pattern.eq(&pattern) {
                            if !hash.eq(&prev_hash.0) { todo!(); }
                            store = false;
                        }
                    }
                    if store {
                        this.output.stored_hash.glob_dependencies.push((path.clone(), pattern, SerializedHash(hash)));
                    }
                }
                result.sort();
                Ok(result)
            },
        );

        methods.add_method_mut(
            "popen",
            |_lua, this, command: Vec<LuaValue>| {
                let mut cmd = Vec::new();
                this.logger.info(format!("running command {}", command.iter().map(|x| x.to_string().unwrap()).collect::<Vec<String>>().join(" ")).as_str());
                for x in command {
                    cmd.push(x.to_string()?);
                }
                Process::create(&cmd)
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
                let tool_file = tool.to_owned() + ".lua";

                for node in &paths {
                    let node = node.make_node(&PathBuf::from(&tool_file));
                    if node.is_file() {
                        let do_run =
                            {
                                let mut this = this.borrow_mut::<Context>()?;
                                if !this.output.tools.iter().any(|x| x == &node) {
                                    this.output.tools.push(node.clone());
                                    true
                                } else {
                                    again.is_some() && again.unwrap()
                                }
                            };

                        if do_run {
                            lua.load(node.abs_path()).call::<AnyUserData, ()>(this)?;
                        }
                        return Ok(());
                    }
                }

                if let Some(file) = TOOLS_DIR.get_file(&tool_file) {
                    let do_run =
                        {
                            let tool_node = Node::from(&PathBuf::from(&tool_file));
                            let mut this = this.borrow_mut::<Context>()?;
                            if !this.output.tools.iter().any(|x| x == &tool_node) {
                                this.output.tools.push(tool_node);
                                true
                            } else {
                                again.is_some() && again.unwrap()
                            }
                        };
                    if do_run {
                        lua.load(file.contents()).set_name(tool_file).call::<AnyUserData, ()>(this)?;
                    }
                    return Ok(());
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
            |lua, (this, name, features, env, group): (AnyUserData, String, LuaValue, Option<AnyUserData>, Option<String>)| {
                if let Some(group) = &group {
                    let context = this.borrow::<Context>()?;
                    if !context.output.groups.iter().any(|x| x.0.eq(&name)) {
                        return Err(LuaError::RuntimeError(format!("When creating generator `{}`: `{}`: group was not declared", &name, group)));
                    }
                }
                let features = match &features {
                    LuaValue::String(s) => s.to_string_lossy().split(',').map(|x| x.trim().to_string()).collect(),
                    LuaValue::Table(_) => { Vec::<String>::from_lua(features, lua)? }
                    LuaValue::Nil => Vec::new(),
                    _ => return Err(LuaError::RuntimeError("features should be a list of string or a single string".to_string())),
                };

                let generator = {
                    let mut this = this.borrow_mut::<Context>()?;
                    let from_env = if let Some(env) = env {
                        env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?.deref().clone()
                    } else {
                        this.environment.clone()
                    };
                    let env = Arc::new(Mutex::new(ReadWriteEnvironment::derive(&from_env, this.output.environments.len())?));
                    this.output.environments.push(env.clone());
                    let group = match group {
                        Some(x) => x,
                        None => this.spec.name.clone(),
                    };
                    lua.create_userdata(Arc::new(Mutex::new(Generator::new(name, env, group, features))))?
                };

                generator.set_named_user_value(":context", &this)?;
                this.named_user_value::<LuaTable>(":generators")?.push(generator.clone())?;
                Ok(generator)
            },
        );

        methods.add_function(
            "feature",
            |lua, (this, feature_names, name, method): (AnyUserData, LuaValue, String, LuaFunction)| {
                let feature_names = match &feature_names {
                    LuaValue::String(s) => s.to_string_lossy().split(',').map(|x| x.trim().to_string()).collect(),
                    LuaValue::Table(_) => { Vec::<String>::from_lua(feature_names, lua)? }
                    LuaValue::Nil => Vec::new(),
                    _ => return Err(LuaError::RuntimeError("features should be a list of string or a single string".to_string())),
                };

                let mut features = this.named_user_value::<Vec<AnyUserData>>(":features")?;
                for f in features.iter() {
                    let feature_name = &f.borrow::<Feature>()?.0;
                    if feature_name.eq(&name) {
                        return Err(LuaError::RuntimeError(format!("Feature {} already defined.", name)));
                    }
                }

                {
                    let mut context = this.borrow_mut::<Context>()?;
                    context.sorted_features.push(name.clone());
                }

                let feature_index = lua.create_userdata(FeatureIndex(features.len()))?;

                let feature = lua.create_any_userdata(Feature(name, feature_names))?;
                feature.set_named_user_value(":call", method)?;
                features.push(feature);
                this.set_named_user_value(":features", features)?;

                feature_index.set_user_value(this)?;

                Ok(feature_index)
            },
        );

        methods.add_function("post", |lua, (this, generator): (AnyUserData, AnyUserData)| post(lua, (&this, &generator)));

        methods.add_method_mut(
            "declare_group",
            |_lua, this, (name, enabled): (String, LuaValue)| {
                if this.output.groups.iter().any(|x| x.0.eq(&name)) {
                    Err(LuaError::RuntimeError(format!("`{}`: build group already registered", &name)))
                } else {
                    let status = match enabled {
                        LuaValue::Nil => GroupStatus::Default,
                        LuaValue::Integer(i) => if i == 0 { GroupStatus::Disabled } else { GroupStatus::Enabled },
                        LuaValue::Boolean(b) => if b { GroupStatus::Enabled } else { GroupStatus::Disabled },
                        LuaValue::String(s) => GroupStatus::Conditional(s.to_string_lossy().to_string()),
                        _ => return Err(LuaError::RuntimeError("Parameter `enabled` of method `declare_group` should be nil, a boolean, or a string".to_string())),
                    };
                    this.output.groups.push((name.clone(), status));
                    Ok(())
                }
            },
        );

        methods.add_method_mut(
            "command_driver",
            |_lua, this, (name, color, command): (String, String, String)| {
                if is_command_valid(command.as_str()) {
                    if this.output.drivers.insert(name.clone(), Driver::from_command(color, command)).is_some() {
                        this.logger.info(format!("Overriding tool {}", name).as_str());
                    }
                    Ok(())
                } else {
                    Err(LuaError::RuntimeError(format!("invalid syntax in command {}", command).to_string()))
                }
            },
        );

        methods.add_method_mut(
            "dependency_driver",
            |_lua, this, (name, color, command): (String, String, String)| {
                if is_command_valid(command.as_str()) {
                    if this.output.drivers.insert(name.clone(), Driver::from_dependency_command(color, command)).is_some() {
                        this.logger.info(format!("Overriding tool {}", name).as_str());
                    }
                    Ok(())
                } else {
                    Err(LuaError::RuntimeError(format!("invalid syntax in command {}", command).to_string()))
                }
            },
        );

        methods.add_method_mut(
            "lua_driver",
            |_lua, this, (name, color, script): (String, String, Node)| {
                if this.output.drivers.insert(name.clone(), Driver::from_lua_script(color, script)).is_some() {
                    this.logger.info(format!("Overriding tool {}", name).as_str());
                }
                Ok(())
            },
        );
    }
}

use crate::task::{SPLIT_RE, ENV_RE};

fn is_command_valid(command: &str) -> bool {
    for argument in SPLIT_RE.split(command) {
        let mut iter = ENV_RE.find_iter(argument);
        if iter.next().is_some() && iter.next().is_some() {
            return false;
        }
    }
    true
}