use super::Context;
use crate::command::{
    Command, CommandHash, CommandOutput, CommandSpec, CommandStatus, GroupStatus, SerializedHash,
    TaskSeq,
};
use crate::context::{TOOLS_DIR, TOOLS_PATH};
use crate::environment::{OverlayMap, RawLookup};
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use lazy_static::lazy_static;
use mlua::prelude::{LuaError, LuaResult, LuaValue};
use mlua::{AnyUserData, Lua, Table};
use regex::Regex;
use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::iter::zip;
use std::mem::swap;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

const ROOT_SCRIPT: &str = "bolt.lua";

lazy_static! {
    pub(crate) static ref INVALID_CHARS: Regex = Regex::new(r"[<>:/\\|\?\*]+").unwrap();
}

pub(super) struct DeclaredCommand {
    pub(super) path: Vec<usize>,
}

pub(super) struct Feature(pub(super) String, pub(super) Vec<String>);

impl Context {
    pub(crate) fn new(
        spec: CommandSpec,
        options_context: Options,
        envs: &[Arc<Mutex<OverlayMap>>],
        command_path: Vec<String>,
    ) -> crate::error::Result<Context> {
        let current_dir = Node::from(&std::env::current_dir()?);
        let bld_dir = if let Options::Environment(options) = &options_context {
            options
                .lock()
                .unwrap()
                .get_node("out", &current_dir)
                .unwrap()
        } else {
            current_dir.clone()
        };
        bld_dir.mkdir()?;
        let mut run_envs = Vec::new();
        {
            let mut done_envs = Vec::new();
            spec.envs.iter().for_each(|&x| {
                OverlayMap::derive_from_parent(&envs[x], &mut run_envs, &mut done_envs);
            });
        }

        let start_env = run_envs[0].clone();
        Ok(Context {
            spec: spec.clone(),
            output: CommandOutput {
                environments: run_envs,
                options: None,
                commands: Vec::new(),
                tools: Vec::new(),
                stored_hash: CommandHash {
                    file_dependencies: Vec::new(),
                    option_dependencies: Vec::new(),
                    variable_dependencies: Vec::new(),
                    glob_dependencies: Vec::new(),
                    hash: None,
                },
                groups: vec![(spec.fs_name.clone(), GroupStatus::Enabled)],
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
            default_group: spec.fs_name.clone(),
            logger: Logger::new(None, 0, false),
            command_path,
            commands: HashMap::new(),
            sorted_features: Vec::new(),
            partial_order: Vec::new(),
            driver_order: Vec::new(),
            driver_tasks: HashMap::new(),
            in_post: 0,
        })
    }

    pub(crate) fn run(
        &mut self,
        envs: &Vec<Arc<Mutex<OverlayMap>>>,
        tools: &Vec<Node>,
        commands: &mut HashMap<String, Vec<String>>,
        mut logger: Logger,
    ) -> crate::error::Result<Logger> {
        swap(commands, &mut self.commands);
        swap(&mut logger, &mut self.logger);

        self.output.drivers.insert(
            "untar".to_string(),
            crate::driver::Driver::untar("cyan".to_string()),
        );
        self.output.drivers.insert(
            "unzip".to_string(),
            crate::driver::Driver::unzip("cyan".to_string()),
        );
        self.output.drivers.insert(
            "patch".to_string(),
            crate::driver::Driver::patch("cyan".to_string()),
        );
        self.output.drivers.insert(
            "copy".to_string(),
            crate::driver::Driver::copy("cyan".to_string()),
        );
        {
            let lua = Lua::new();
            let globals = lua.globals();

            let run = |userdata: &mut AnyUserData, path| -> LuaResult<()> {
                let chunk = lua.load(path);
                chunk.call(userdata.clone())
            };
            let run_content = |userdata: &mut AnyUserData, tool_path: &PathBuf| -> LuaResult<()> {
                let chunk = lua
                    .load(TOOLS_DIR.get_file(tool_path).unwrap().contents())
                    .set_name(format!(
                        "@{}",
                        PathBuf::from(TOOLS_PATH)
                            .join("tools")
                            .join(tool_path)
                            .display(),
                    ));
                chunk.call(userdata.clone())
            };

            let mut root_path = std::env::current_dir()?.join(ROOT_SCRIPT);
            if !root_path.is_file() {
                root_path = std::env::current_dir()?.join(PathBuf::from(&self.spec.fs_name));
                root_path.set_extension("lua");
            }
            if !root_path.is_file() {
                return Err(format!(
                    "main script {} or {} not found in {:?}",
                    ROOT_SCRIPT,
                    self.spec.fs_name,
                    std::env::current_dir()?
                )
                .into());
            }
            self.output
                .stored_hash
                .file_dependencies
                .push(root_path.clone());
            lua.scope(|scope| {
                let mut userdata = scope.create_userdata_ref_mut::<Context>(self).unwrap();
                userdata.set_named_user_value(":features", lua.create_table()?)?;
                userdata.set_named_user_value(":generators", lua.create_table()?)?;
                for path in tools {
                    if userdata.borrow_mut_scoped::<Context, _>(|this| {
                        let do_run = !this.output.tools.iter().any(|x| x.eq(path));
                        if do_run {
                            this.output.tools.push(path.clone());
                        }
                        do_run
                    })? {
                        if path.is_file() {
                            run(&mut userdata, path.abs_path())?;
                        } else {
                            run_content(&mut userdata, path.path())?;
                        }
                    }
                }

                run(&mut userdata, root_path.as_path())?;

                userdata.borrow_mut_scoped::<Context, _>(|this| {
                    this.in_post = 1;
                })?;
                let mut generator_count = 0;
                loop {
                    let generators =
                        userdata.named_user_value::<Vec<AnyUserData>>(":generators")?;
                    if generators.len() == generator_count {
                        break;
                    }
                    for generator in &generators[generator_count..] {
                        super::feature::post(&lua, (&userdata, &generator))?;
                    }
                    generator_count = generators.len();
                }

                Ok(())
            })?;

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
            self.output
                .stored_hash
                .variable_dependencies
                .push(env.lock().unwrap().get_used_keys())
        }
        if let Options::Environment(e) = &self.options {
            self.output.options = Some(e.lock().unwrap().clone());
            self.output.stored_hash.option_dependencies =
                e.lock().unwrap().get_used_keys().iter().cloned().collect();
        }

        if self.tasks.is_empty() {
            self.output.tasks = TaskSeq::None;
        } else {
            let mut result_tasks = Vec::new();
            swap(&mut result_tasks, &mut self.tasks);
            self.output.tasks = TaskSeq::List(result_tasks);
        }

        self.output.stored_hash.hash = Some(self.output.hash(
            self.output.options.as_ref(),
            envs,
            &self.output.tools,
        )?);
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
                    fs_name: INVALID_CHARS.replace_all(name, "_").to_string(),
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
                    fs_name: INVALID_CHARS.replace_all(name, "_").to_string(),
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
                let mut result = path.path.clone();
                result.push(cmd.output.as_ref().unwrap().commands.len() - 1);
                Ok(result)
            }
        }
    }
}
