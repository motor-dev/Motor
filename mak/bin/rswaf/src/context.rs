use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs;
use std::mem::swap;
use std::ops::Deref;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use blake3::Hasher;
use mlua::prelude::{LuaError, LuaFunction, LuaResult, LuaString, LuaValue};
use mlua::{AnyUserData, FromLua, IntoLua, MetaMethod, UserData, UserDataFields, UserDataMethods};
use crate::command::{Command, CommandOutput};
use crate::environment::Environment;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use crate::subprocess::Popen;

pub(crate) struct Context {
    pub(crate) spec: crate::command::CommandSpec,
    pub(crate) output: CommandOutput,
    pub(crate) environment: Arc<Mutex<Environment>>,
    pub(crate) path: Node,
    pub(crate) src_dir: Node,
    pub(crate) bld_dir: Node,
    pub(crate) options: Options,
    pub(crate) logger: Logger,
    pub(crate) command_path: Vec<String>,
    pub(crate) commands: HashMap<String, Vec<String>>,
}

struct DeclaredCommand {
    path: Vec<usize>,
}

impl Context {
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
                let spec = crate::command::CommandSpec {
                    name: name.to_string(),
                    function: function.to_string(),
                    envs,
                };
                self.output.commands.push(Command {
                    spec,
                    output: None,
                    up_to_date: false,
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
                let spec = crate::command::CommandSpec {
                    name: name.to_string(),
                    function: function.to_string(),
                    envs: Vec::new(),
                };
                if cmd.output.is_none() {
                    cmd.output = Some(CommandOutput {
                        environments: Vec::new(),
                        commands: Vec::new(),
                        options: None,
                        stored_hash: crate::command::CommandHash {
                            file_dependencies: Vec::new(),
                            option_dependencies: Vec::new(),
                            variable_dependencies: Vec::new(),
                            glob_dependencies: Vec::new(),
                            hash: None,
                        },
                    });
                }
                cmd.output.as_mut().unwrap().commands.push(Command {
                    spec,
                    output: None,
                    up_to_date: false,
                });
                full_path.push(name.to_string());
                v.insert(full_path);
                Ok(vec![self.output.commands.len()])
            }
        }
    }
}

impl UserData for DeclaredCommand {}

impl UserData for Context {
    fn add_fields<'lua, F: UserDataFields<'lua, Self>>(fields: &mut F) {
        fields.add_field_method_get("name", |_, this| Ok(this.spec.name.clone()));
        fields.add_field_method_get("fun", |_, this| Ok(this.spec.function.clone()));
        fields.add_field_method_get("env", |_, this| Ok(this.environment.clone()));
        fields.add_field_method_get("envs", |_, this| Ok(this.output.environments.clone()));
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
            let result: LuaResult<()> = lua.load(script.abspath()).call(&args.0);
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
                            env.borrow::<Arc<Mutex<Environment>>>()?
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
                        .borrow::<Arc<Mutex<Environment>>>()?;
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
            let env_ref = env.borrow::<Arc<Mutex<Environment>>>()?;
            let new_env = Arc::new(Mutex::new(Environment::derive(
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
        methods.add_method_mut("warn", |_lua, this, message: String| {
            this.logger.warning(message.as_str());
            Ok(())
        });
        methods.add_method_mut("error", |_lua, this, message: String| {
            this.logger.error(message.as_str());
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
        methods.add_method_mut("fatal", |_lua, _this, message: String| -> LuaResult<()> {
            Err(LuaError::RuntimeError(message))
        });
        methods.add_function_mut(
            "with",
            |_lua, (context, env, function): (AnyUserData, AnyUserData, LuaFunction)| {
                let prev_env = {
                    let mut context = context.borrow_mut::<Context>()?;
                    let env = env.borrow_mut::<Arc<Mutex<Environment>>>()?;
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
            |_lua, this, (path, pattern): (AnyUserData, String)| {
                let path = path.borrow::<Node>()?;
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
                        if prev_path.path().eq(path.path()) && prev_pattern.eq(&pattern) {
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
    }
}
