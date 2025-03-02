use super::serialization::TaskSequenceSeed;
use super::{Command, CommandOutput, CommandSpec, CommandStatus, TaskSeq};
use crate::context::Context;
use crate::environment::{FlatMap, OverlayMap};
use crate::error::Result;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use blake3::Hasher;
use std::collections::HashMap;
use std::mem::swap;
use std::sync::{Arc, Mutex};

impl Command {
    pub(crate) fn is_up_to_date(&self) -> bool {
        matches!(&self.status, CommandStatus::UpToDate)
    }

    pub(crate) fn get_run_options(&self) -> Option<&FlatMap> {
        if let Some(output) = &self.output {
            output.options.as_ref()
        } else {
            None
        }
    }

    pub(crate) fn verify_hash(
        &mut self,
        options: &FlatMap,
        envs: &[Arc<Mutex<OverlayMap>>],
        mut tools: Vec<Node>,
    ) -> std::result::Result<(), String> {
        if let Some(output) = &mut self.output {
            let mut tasks = TaskSeq::None;
            if let TaskSeq::Cached(tasks_file) = &output.tasks {
                if let Ok(buffer) = std::fs::read(tasks_file) {
                    let task_result = bincode::serde::decode_seed_from_slice(
                        TaskSequenceSeed(&mut output.environments),
                        buffer.as_slice(),
                        bincode::config::standard(),
                    );
                    //let tasks = TaskSequenceSeed(&output.environments)
                    //   .deserialize(&mut serde_json::Deserializer::from_slice(buffer.as_slice()));
                    if let Ok(task_list) = task_result {
                        tasks = TaskSeq::List(task_list);
                    } else {
                        return Err(format!(
                            "the tasks cache `{}` could not be deserialized.",
                            tasks_file.to_string_lossy()
                        ));
                    }
                } else {
                    return Err(format!(
                        "the tasks cache `{}` is missing or can't be opened for read.",
                        tasks_file.to_string_lossy()
                    ));
                }
            }

            if let Some(stored_hash) = &output.stored_hash.hash {
                for node in &output.tools {
                    if !tools.contains(node) {
                        tools.push(node.clone());
                    }
                }

                let hash_result = output.hash(Some(options), envs, &tools);
                if let Ok(hash) = hash_result {
                    if !hash.0 .0.eq(&stored_hash.0 .0) {
                        return Err("files have changed on disc".to_string());
                    } else if !hash.1 .0.eq(&stored_hash.1 .0) {
                        return Err("tools implementation have changed".to_string());
                    } else if !hash.2 .0.eq(&stored_hash.2 .0) {
                        return Err("command-line options have changed".to_string());
                    } else if !hash.3 .0.eq(&stored_hash.3 .0) {
                        return Err("the environment has changed".to_string());
                    } else {
                        for (path, pattern, hash) in &output.stored_hash.glob_dependencies {
                            if !path.is_dir() {
                                let hasher = Hasher::new();
                                if !hasher.finalize().eq(&hash.0) {
                                    return Err(format!(
                                        "the result of file search `{}/{}` has changed.",
                                        path.path().to_string_lossy(),
                                        pattern
                                    ));
                                }
                            } else {
                                let search_string = path.path().join(pattern);
                                let search_string = &*search_string.to_string_lossy();
                                let paths = glob::glob(search_string).unwrap();
                                let mut hasher = Hasher::new();
                                let mut result = paths.flatten().collect::<Vec<_>>();
                                result.sort();
                                for path in result {
                                    hasher.update(path.as_os_str().as_encoded_bytes());
                                }
                                if !hasher.finalize().eq(&hash.0) {
                                    return Err(format!(
                                        "the result of file search `{}` has changed.",
                                        search_string
                                    ));
                                }
                            }
                        }
                    }
                    output.tasks = tasks;
                    for env in &output.environments {
                        let mut env = env.lock().unwrap();
                        env.update_parent(envs);
                    }
                    Ok(())
                } else {
                    Err("the hash could not be computed".to_string())
                }
            } else {
                Err("the hash does not exist".to_string())
            }
        } else {
            Err("the command was never run".to_string())
        }
    }

    pub(crate) fn run(
        &mut self,
        options_context: Options,
        envs: &Vec<Arc<Mutex<OverlayMap>>>,
        tools: &Vec<Node>,
        command_path: Vec<String>,
        commands: &mut HashMap<String, Vec<String>>,
        logger: Logger,
    ) -> Result<Logger> {
        commands.retain(|_, v| !v.starts_with(command_path.as_slice()));
        let mut context = Context::new(self.spec.clone(), options_context, envs, command_path)?;
        let logger = context.run(envs, tools, commands, logger)?;

        if let Some(output) = &mut self.output {
            swap(output, &mut context.output);
            self.merge_cache(context.output.commands, commands);
        } else {
            self.output = Some(context.output);
        }

        self.status = CommandStatus::UpToDate;
        Ok(logger)
    }

    pub(super) fn merge_cache(
        &mut self,
        cache: Vec<Command>,
        command_map: &mut HashMap<String, Vec<String>>,
    ) {
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
        if let CommandStatus::ForwardDeclared = &self.status {
            self.spec = cached_spec;
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
                        if let Some(index) = output
                            .commands
                            .iter()
                            .position(|x| x.spec.name.eq(&new_cmd.spec.name))
                        {
                            output.commands[index].merge_with(
                                new_cmd.spec,
                                new_cmd.output,
                                command_map,
                                path,
                            );
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
}
