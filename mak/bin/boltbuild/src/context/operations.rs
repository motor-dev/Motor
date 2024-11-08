use super::Context;

use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::iter::zip;
use std::mem::swap;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use mlua::{AnyUserData, Lua, Table};
use mlua::prelude::{LuaError, LuaFunction, LuaResult, LuaValue};

use crate::command::{Command, CommandHash, CommandOutput, CommandSpec, CommandStatus, GroupStatus, SerializedHash, TaskSeq};
use crate::environment::ReadWriteEnvironment;
use crate::generator::Generator;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use crate::context::TOOLS_DIR;

const ROOT_SCRIPT: &str = "make.lua";

pub(super) struct DeclaredCommand {
    pub(super) path: Vec<usize>,
}

pub(super) struct Feature(pub(super) String, pub(super) Vec<String>);

impl Context {
    pub(crate) fn new(
        spec: CommandSpec,
        options_context: Options,
        envs: &[Arc<Mutex<ReadWriteEnvironment>>],
        command_path: Vec<String>,
    ) -> crate::error::Result<Context> {
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
                tools: Vec::new(),
                stored_hash: CommandHash {
                    file_dependencies: Vec::new(),
                    option_dependencies: Vec::new(),
                    variable_dependencies: Vec::new(),
                    glob_dependencies: Vec::new(),
                    hash: None,
                },
                groups: vec![(spec.name.clone(), GroupStatus::Enabled)],
                tasks: TaskSeq::None,
                drivers: HashMap::new(),
            },
            environment: start_env,
            tasks: Vec::new(),
            products: HashMap::new(),
            signatures: Vec::new(),
            task_dependencies: Vec::new(),
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
    ) -> crate::error::Result<Logger> {
        swap(commands, &mut self.commands);
        swap(&mut logger, &mut self.logger);

        {
            let lua = Lua::new();
            let globals = lua.globals();

            let run = |userdata: &mut AnyUserData, path| -> LuaResult<()> {
                let chunk = lua.load(path);
                chunk.call(userdata.clone())
            };
            let run_content = |userdata: &mut AnyUserData, tool_path: &PathBuf| -> LuaResult<()> {
                let chunk = lua.load(TOOLS_DIR.get_file(tool_path).unwrap().contents()).set_name(tool_path.to_string_lossy());
                chunk.call(userdata.clone())
            };

            self.output.stored_hash.file_dependencies.push(ROOT_SCRIPT.into());
            lua.scope(|scope| {
                let mut userdata = scope.create_userdata_ref_mut(self).unwrap();
                userdata.set_named_user_value(":features", lua.create_table()?)?;
                userdata.set_named_user_value(":generators", lua.create_table()?)?;
                for path in tools {
                    if !userdata.borrow_mut::<Context>()?.output.tools.iter().any(|x| x.eq(path))
                    {
                        userdata.borrow_mut::<Context>()?.output.tools.push(path.clone());
                        if path.is_file() {
                            run(&mut userdata, path.abs_path())?;
                        } else {
                            run_content(&mut userdata, path.path())?;
                        }
                    }
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

            for &(predecessor, successor) in &self.task_dependencies {
                self.tasks[predecessor].successors.push(successor);
                self.tasks[successor].predecessors.push(predecessor);
            }
            for (hasher, task) in zip(&self.signatures, &mut self.tasks) {
                task.signature = SerializedHash(hasher.finalize());
                let mut env = task.env.lock().unwrap();
                env.set("SRC", (&task.inputs).into());
                env.set("TGT", (&task.outputs).into());
            }

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
                    .cloned()
                    .collect(),
            )
        }
        if let Some(options_env) = &self.output.options {
            self.output.stored_hash.option_dependencies = options_env
                .used_keys
                .iter()
                .cloned()
                .collect();
        }

        if self.tasks.is_empty() {
            self.output.tasks = TaskSeq::None;
        } else {
            let mut result_tasks = Vec::new();
            swap(&mut result_tasks, &mut self.tasks);
            self.output.tasks = TaskSeq::List(result_tasks);
        }

        self.output.stored_hash.hash = Some(self.output.hash(self.output.options.as_ref(), envs, &self.output.tools)?);
        swap(commands, &mut self.commands);
        swap(&mut logger, &mut self.logger);

        Ok(logger)
    }

    pub(super) fn declare_command(
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

    pub(super) fn declare_chain(
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
                for &index in path.path.iter().skip(1) {
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
                        tasks: TaskSeq::None,
                        drivers: HashMap::new(),
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

pub(crate) fn post(_lua: &Lua, (this, generator): (&AnyUserData, &AnyUserData)) -> LuaResult<()> {
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
                    if feature.1.iter().any(|x| x.eq(f)) {
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
        let result = callback.call::<&AnyUserData, ()>(generator);
        {
            let mut owner = this.borrow_mut::<Context>()?;
            owner.in_post -= 1;
        }
        result?;
    }

    Ok(())
}
