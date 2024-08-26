use super::{Command, CommandSpec, CommandOutput, CommandStatus};
use crate::environment::{Environment, ReadWriteEnvironment};
use crate::error::Result;
use crate::log::Logger;
use crate::node::Node;
use crate::options::{CommandLineParser, Options};
use crate::context::Context;
use blake3::{Hasher};
use std::collections::HashMap;
use std::fmt;
use std::mem::swap;
use std::ops::Deref;
use std::sync::{Arc, Mutex};


impl Command {
    pub(crate) fn init() -> Result<Self> {
        let init_command = Command {
            spec: CommandSpec::create_init(),
            output: None,
            status: CommandStatus::Defined,
        };
        Ok(init_command)
    }

    pub(crate) fn run_with_deps<Iter>(
        &mut self,
        mut path: Iter,
        envs: &Vec<Arc<Mutex<ReadWriteEnvironment>>>,
        tools: &Vec<Node>,
        options: &Environment,
        command_line: Arc<Mutex<CommandLineParser>>,
        mut current_path: Vec<String>,
        registered_commands: &mut HashMap<String, Vec<String>>,
        mut logger: Logger,
        run_implicit: bool,
    ) -> Result<Logger>
    where
        Iter: Iterator,
        <Iter as Iterator>::Item: PartialEq<String>,
        <Iter as Iterator>::Item: fmt::Display,
    {
        current_path.push(self.spec.name.clone());
        let next_item = path.next();

        match &self.status {
            CommandStatus::UpToDate => {}
            _ => {
                let options = if run_implicit || next_item.is_some() {
                    if let Some(output) = &self.output {
                        if let Some(options) = &output.options {
                            let mut options = options.clone();
                            command_line
                                .lock()
                                .unwrap()
                                .parse_command_line_into(&mut options);
                            options
                        } else { options.clone() }
                    } else { options.clone() }
                } else { options.clone() };

                let do_run = if let Some(output) = &mut self.output {
                    if let Some(stored_hash) = &output.stored_hash.hash {
                        let mut tools_list = tools.clone();
                        for node in &output.tools {
                            if !tools.contains(node) {
                                tools_list.push(node.clone());
                            }
                        }
                        let hash_result = output.hash(Some(&options), envs, &tools_list);
                        if let Ok(hash) = hash_result {
                            if !hash.0.0.eq(&stored_hash.0.0) {
                                logger.why(
                                    format!(
                                        "evaluating command `{}` because files have changed on disc",
                                        self.spec.name
                                    ).as_str(),
                                );
                                true
                            } else if !hash.1.0.eq(&stored_hash.1.0) {
                                logger.why(
                                    format!(
                                        "evaluating command `{}` because tools implementation have changed",
                                        self.spec.name
                                    ).as_str(),
                                );
                                true
                            } else if !hash.2.0.eq(&stored_hash.2.0) {
                                logger.why(
                                    format!(
                                        "evaluating command `{}` because command-line options have changed",
                                        self.spec.name
                                    ).as_str(),
                                );
                                true
                            } else if !hash.3.0.eq(&stored_hash.3.0) {
                                logger.why(
                                    format!(
                                        "evaluating command `{}` because the environment has changed",
                                        self.spec.name
                                    ).as_str(),
                                );
                                true
                            } else {
                                let mut pattern_changed = false;
                                for (path, pattern, hash) in &output.stored_hash.glob_dependencies {
                                    if !path.is_dir() {
                                        logger.why(
                                            format!(
                                                "evaluating command `{}` because the directory `{}` used in file search `{}` has been deleted.",
                                                self.spec.name,
                                                path.path().to_string_lossy(),
                                                pattern
                                            ).as_str(),
                                        );
                                        pattern_changed = true;
                                        break;
                                    } else {
                                        let paths = glob::glob(
                                            path.path()
                                                .join(&pattern)
                                                .to_string_lossy()
                                                .deref()
                                        ).unwrap();
                                        let mut hasher = Hasher::new();
                                        for path in paths {
                                            if let Ok(path) = path {
                                                hasher.update(path.as_os_str().as_encoded_bytes());
                                            }
                                        }
                                        if !hasher.finalize().eq(&hash.0) {
                                            logger.why(
                                                format!(
                                                    "evaluating command `{}` because the result of file search `{}/{}` has changed.",
                                                    self.spec.name,
                                                    path.path().to_string_lossy(),
                                                    pattern
                                                ).as_str(),
                                            );
                                            pattern_changed = true;
                                            break;
                                        }
                                    }
                                }
                                pattern_changed
                            }
                        } else {
                            logger.why(
                                format!(
                                    "evaluating command `{}` because the hash could not be computed",
                                    self.spec.name
                                ).as_str(),
                            );
                            true
                        }
                    } else {
                        logger.why(
                            format!(
                                "evaluating command `{}` because the hash does not exist",
                                self.spec.name
                            ).as_str(),
                        );
                        true
                    }
                } else {
                    logger.why(
                        format!(
                            "evaluating command `{}` because the command was never run",
                            self.spec.name
                        ).as_str(),
                    );
                    true
                };

                if do_run {
                    logger = self.run(
                        Options::from_env(options),
                        envs,
                        tools,
                        current_path.clone(),
                        registered_commands,
                        logger,
                    )?;
                } else {
                    self.status = CommandStatus::UpToDate;
                    if next_item.is_none() {
                        logger.why(format!("`{}` is up-to-date", self.spec.name).as_str());
                    }
                }
            }
        }

        if let Some(output) = self.output.as_mut() {
            if let Some(cmd_name) = next_item {
                for command in &mut output.commands {
                    if cmd_name.eq(&command.spec.name) {
                        return command.run_with_deps(
                            path,
                            &output.environments,
                            &output.tools,
                            options,
                            command_line,
                            current_path,
                            registered_commands,
                            logger,
                            run_implicit,
                        );
                    }
                }
                Err(format!("command '{}' not defined", cmd_name).into())
            } else {
                Ok(logger)
            }
        } else {
            Err(format!("command '{}' did not generate any output", self.spec.name).into())
        }
    }

    pub(super) fn merge_cache(&mut self, cache: Vec<Command>, command_map: &mut HashMap<String, Vec<String>>) {
        let mut path = vec![self.spec.name.clone()];
        for command in cache {
            for declared_command in &mut self.output.as_mut().unwrap().commands {
                if declared_command.spec.name.eq(&command.spec.name) {
                    declared_command.merge_with(
                        command.spec,
                        command.output,
                        command_map,
                        &mut path,
                    );
                    break;
                }
            }
        }
    }

    fn merge_with(
        &mut self,
        cached_spec: CommandSpec,
        cached_output: Option<CommandOutput>,
        command_map: &mut HashMap<String, Vec<String>>,
        path: &mut Vec<String>,
    ) {
        match &self.status {
            CommandStatus::ForwardDeclared => { self.spec = cached_spec; }
            _ => ()
        }
        path.push(self.spec.name.clone());
        match &mut self.output {
            None => {
                if let Some(output) = &cached_output {
                    for new_cmd in &output.commands {
                        new_cmd.register(command_map, path);
                    }
                }
                self.output = cached_output;
            }
            Some(output) => {
                if let Some(cached_output) = cached_output {
                    output.environments = cached_output.environments;
                    output.tools = cached_output.tools;
                    output.options = cached_output.options;
                    output.stored_hash = cached_output.stored_hash;

                    for new_cmd in cached_output.commands {
                        if let Some(index) = output.commands
                            .iter()
                            .position(|x| x.spec.name.eq(&new_cmd.spec.name))
                        {
                            output.commands[index].merge_with(new_cmd.spec, new_cmd.output, command_map, path);
                        } else {
                            new_cmd.register(command_map, path);
                            output.commands.push(new_cmd);
                        }
                    }
                }
            }
        }
        path.pop();
    }

    fn register(&self, command_map: &mut HashMap<String, Vec<String>>, path: &mut Vec<String>) {
        path.push(self.spec.name.clone());
        command_map.insert(self.spec.name.clone(), path.clone());
        if let Some(output) = &self.output {
            for command in &output.commands {
                command.register(command_map, path);
            }
        }
        path.pop();
    }

    pub(crate) fn run(
        &mut self,
        options_context: Options,
        envs: &Vec<Arc<Mutex<ReadWriteEnvironment>>>,
        tools: &Vec<Node>,
        command_path: Vec<String>,
        commands: &mut HashMap<String, Vec<String>>,
        logger: Logger,
    ) -> Result<Logger> {
        commands.retain(|_, v| !v.starts_with(command_path.as_slice()));
        let mut cmd = Context::new(self.spec.clone(), options_context, envs, tools, command_path)?;
        let logger = cmd.run(envs, tools, commands, logger)?;

        if let Some(output) = &mut self.output {
            swap(&mut output.commands, &mut cmd.output.commands);
            output.tools = cmd.output.tools;
            output.options = cmd.output.options;
            output.environments = cmd.output.environments;
            output.stored_hash = cmd.output.stored_hash;
            self.merge_cache(cmd.output.commands, commands);
        } else {
            self.output = Some(cmd.output);
        }

        self.status = CommandStatus::UpToDate;
        Ok(logger)
    }
}
