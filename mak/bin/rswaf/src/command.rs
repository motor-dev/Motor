use crate::environment::{
    Environment,
    ReadWriteEnvironment, ReadWriteEnvironmentSequenceSeed, SerializedReadWriteEnvironment,
};
use crate::error::Result;
use crate::log::Logger;
use crate::node::Node;
use crate::options::{CommandLineParser, Options};
use crate::context::Context;
use blake3::{Hash, Hasher};
use serde::de::{DeserializeSeed, Error, MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use serde::ser::SerializeStruct;
use std::collections::HashMap;
use std::fmt;
use std::iter::zip;
use std::mem::swap;
use std::ops::Deref;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

use std::result::Result as StdResult;


#[derive(Serialize, Deserialize)]
pub(crate) enum CommandStatus {
    ForwardDeclared,
    Defined,
    Cached,
    UpToDate,
}

#[derive(Serialize)]
pub(crate) struct Command {
    pub(crate) spec: CommandSpec,
    pub(crate) output: Option<CommandOutput>,
    pub(crate) status: CommandStatus,
}

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

    pub(crate) fn load_from_file(
        &mut self,
        file: std::fs::File,
        command_map: &mut HashMap<String, Vec<String>>,
    ) -> Result<()> {
        struct CommandCacheSeed(Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

        impl<'de> DeserializeSeed<'de> for CommandCacheSeed {
            type Value = Vec<Command>;

            fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
            where
                D: Deserializer<'de>,
            {
                struct CommandCacheVisitor(Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

                impl<'de> Visitor<'de> for CommandCacheVisitor {
                    type Value = Vec<Command>;

                    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                        formatter.write_str("sequence of Command")
                    }

                    fn visit_seq<V>(mut self, mut seq: V) -> StdResult<Vec<Command>, V::Error>
                    where
                        V: SeqAccess<'de>,
                    {
                        let mut result = Vec::new();
                        if let Some(size_hint) = seq.size_hint() {
                            result.reserve(size_hint);
                        }
                        while let Some(elem) = seq.next_element_seed(CommandSeed(&mut self.0))? {
                            result.push(elem);
                        }
                        Ok(result)
                    }
                }

                deserializer.deserialize_seq(CommandCacheVisitor(self.0))
            }
        }

        let envs = vec![self.output.as_ref().unwrap().environments.clone()];
        let reader = std::io::BufReader::new(file);
        let commands = CommandCacheSeed(envs)
            .deserialize(&mut serde_json::Deserializer::from_reader(reader))?;
        self.merge_cache(commands, command_map);
        Ok(())
    }

    pub(crate) fn save_to_file(&self, file: std::fs::File) -> Result<()> {
        Ok(serde_json::to_writer_pretty(
            file,
            &self.output.as_ref().unwrap().commands,
        )?)
    }

    fn merge_cache(&mut self, cache: Vec<Command>, command_map: &mut HashMap<String, Vec<String>>) {
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

pub(crate) struct CommandSeed<'a>(pub &'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

impl<'de, 'a> DeserializeSeed<'de> for CommandSeed<'a> {
    type Value = Command;

    fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Spec,
            Output,
            Status,
        }

        impl<'de> Deserialize<'de> for Field {
            fn deserialize<D>(deserializer: D) -> StdResult<Field, D::Error>
            where
                D: Deserializer<'de>,
            {
                struct FieldVisitor;

                impl<'de> Visitor<'de> for FieldVisitor {
                    type Value = Field;

                    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                        formatter.write_str("`spec`, `output` or `status`")
                    }

                    fn visit_str<E>(self, value: &str) -> StdResult<Field, E>
                    where
                        E: Error,
                    {
                        match value {
                            "spec" => Ok(Field::Spec),
                            "output" => Ok(Field::Output),
                            "status" => Ok(Field::Status),
                            _ => Err(Error::unknown_field(value, &["spec", "output", "status"])),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct CommandVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

        impl<'de, 'a> Visitor<'de> for CommandVisitor<'a> {
            type Value = Command;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct Command")
            }

            fn visit_seq<V>(self, mut seq: V) -> StdResult<Command, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let spec = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let output = seq
                    .next_element_seed(CommandOutputSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let status = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let status = match status {
                    CommandStatus::UpToDate => CommandStatus::Cached,
                    other => other
                };
                Ok(Command {
                    spec,
                    output,
                    status,
                })
            }

            fn visit_map<V>(self, mut map: V) -> StdResult<Command, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut spec = None;
                let mut output = None;
                let mut status = None;
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Spec => {
                            if spec.is_some() {
                                return Err(Error::duplicate_field("spec"));
                            }
                            spec = Some(map.next_value()?);
                        }
                        Field::Output => {
                            if output.is_some() {
                                return Err(Error::duplicate_field("output"));
                            }
                            output = Some(map.next_value_seed(CommandOutputSeed(self.0))?);
                        }
                        Field::Status => {
                            if status.is_some() {
                                return Err(Error::duplicate_field("status"));
                            }
                            status = Some(map.next_value()?);
                        }
                    }
                }
                let spec = spec.ok_or_else(|| Error::missing_field("spec"))?;
                let output = output.ok_or_else(|| Error::missing_field("output"))?;
                let status = status.ok_or_else(|| Error::missing_field("status"))?;
                let status = match status {
                    CommandStatus::UpToDate => CommandStatus::Cached,
                    other => other
                };
                Ok(Command {
                    spec,
                    output,
                    status,
                })
            }
        }

        deserializer.deserialize_struct("Command", &["spec", "output"], CommandVisitor(self.0))
    }
}

struct CommandSequenceSeed<'a>(&'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

impl<'de, 'a> DeserializeSeed<'de> for CommandSequenceSeed<'a> {
    type Value = Vec<Command>;

    fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct CommandSequenceVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

        impl<'de, 'a> Visitor<'de> for CommandSequenceVisitor<'a> {
            type Value = Vec<Command>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("sequence of Command")
            }

            fn visit_seq<V>(self, mut seq: V) -> StdResult<Vec<Command>, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let mut result = Vec::new();
                if let Some(size_hint) = seq.size_hint() {
                    result.reserve(size_hint);
                }
                while let Some(elem) = seq.next_element_seed(CommandSeed(self.0))? {
                    result.push(elem);
                }
                Ok(result)
            }
        }

        deserializer.deserialize_seq(CommandSequenceVisitor(self.0))
    }
}

#[derive(Clone, Serialize, Deserialize)]
pub(crate) struct CommandSpec {
    pub(crate) name: String,
    pub(crate) function: String,
    pub(crate) envs: Vec<usize>,
}

impl CommandSpec {
    fn create_init() -> Self {
        Self {
            name: "init".to_string(),
            function: "init".to_string(),
            envs: vec![0],
        }
    }
}

pub(crate) struct CommandOutput {
    pub(crate) environments: Vec<Arc<Mutex<ReadWriteEnvironment>>>,
    pub(crate) commands: Vec<Command>,
    pub(crate) options: Option<Environment>,
    pub(crate) tools: Vec<Node>,
    pub(crate) stored_hash: CommandHash,
}

impl CommandOutput {
    pub(crate) fn hash(
        &self,
        options: Option<&Environment>,
        envs: &Vec<Arc<Mutex<ReadWriteEnvironment>>>,
        tools: &Vec<Node>,
    ) -> std::io::Result<(SerializedHash, SerializedHash, SerializedHash, SerializedHash)> {
        let hash1 = {
            let mut hasher = Hasher::new();
            for file in &self.stored_hash.file_dependencies {
                hasher.update(file.as_os_str().as_encoded_bytes());
                hasher.update_reader(std::fs::File::open(file)?)?;
            }
            SerializedHash(hasher.finalize())
        };

        let hash2 = {
            let mut hasher = Hasher::new();
            for file in tools {
                hasher.update(file.path().as_os_str().as_encoded_bytes());
                hasher.update_reader(std::fs::File::open(file.path())?)?;
            }
            SerializedHash(hasher.finalize())
        };

        let hash3 = {
            let mut hasher = Hasher::new();
            if let Some(env) = options {
                for env_var in &self.stored_hash.option_dependencies {
                    env.get_raw(env_var.as_str()).hash(&mut hasher);
                }
            }
            SerializedHash(hasher.finalize())
        };

        let hash4 = {
            let mut hasher = Hasher::new();
            for (vars, env_arc) in zip(self.stored_hash.variable_dependencies.iter(), envs.iter()) {
                let env = env_arc.lock().unwrap();
                for var in vars {
                    env.get_raw(var.as_str()).hash(&mut hasher);
                }
            }
            SerializedHash(hasher.finalize())
        };

        Ok((hash1, hash2, hash3, hash4))
    }
}

impl Serialize for CommandOutput {
    fn serialize<S>(&self, serializer: S) -> StdResult<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut s = serializer.serialize_struct("Command", 4)?;
        s.serialize_field(
            "environments",
            &self
                .environments
                .iter()
                .map(|v| SerializedReadWriteEnvironment(v))
                .collect::<Vec<SerializedReadWriteEnvironment>>(),
        )?;
        s.serialize_field("commands", &self.commands)?;
        s.serialize_field("options", &self.options)?;
        s.serialize_field("tools", &self.tools)?;
        s.serialize_field("stored_hash", &self.stored_hash)?;
        s.end()
    }
}

struct CommandOutputSeed<'a>(&'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

impl<'de, 'a> DeserializeSeed<'de> for CommandOutputSeed<'a> {
    type Value = Option<CommandOutput>;

    fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Environments,
            Commands,
            Options,
            Tools,
            StoredHash,
        }

        impl<'de> Deserialize<'de> for Field {
            fn deserialize<D>(deserializer: D) -> StdResult<Field, D::Error>
            where
                D: Deserializer<'de>,
            {
                struct FieldVisitor;

                impl<'de> Visitor<'de> for FieldVisitor {
                    type Value = Field;

                    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                        formatter
                            .write_str("`environments`, `commands`, `options` or `stored_hash`")
                    }

                    fn visit_str<E>(self, value: &str) -> StdResult<Field, E>
                    where
                        E: Error,
                    {
                        match value {
                            "environments" => Ok(Field::Environments),
                            "commands" => Ok(Field::Commands),
                            "options" => Ok(Field::Options),
                            "tools" => Ok(Field::Tools),
                            "stored_hash" => Ok(Field::StoredHash),
                            _ => Err(Error::unknown_field(
                                value,
                                &["environments", "commands", "options", "stored_hash"],
                            )),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct CommandOutputVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

        impl<'de, 'a> Visitor<'de> for CommandOutputVisitor<'a> {
            type Value = Option<CommandOutput>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct CommandOutput")
            }

            fn visit_none<E>(self) -> StdResult<Self::Value, E>
            where
                E: Error,
            {
                Ok(None)
            }

            fn visit_some<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
            where
                D: Deserializer<'de>,
            {
                deserializer.deserialize_struct(
                    "Command",
                    &["environments", "commands", "options", "tools", "stored_hash"],
                    self,
                )
            }

            fn visit_seq<V>(self, mut seq: V) -> StdResult<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                (*self.0).push(Vec::new());
                seq.next_element_seed(ReadWriteEnvironmentSequenceSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let commands = seq
                    .next_element_seed(CommandSequenceSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(1, &self))?;
                let options = seq
                    .next_element::<Option<Environment>>()?
                    .ok_or_else(|| Error::invalid_length(2, &self))?;
                let tools = seq
                    .next_element::<Vec<Node>>()?
                    .ok_or_else(|| Error::invalid_length(3, &self))?;
                let stored_hash = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(4, &self))?;
                let environments = self.0.pop().unwrap();
                Ok(Some(CommandOutput {
                    environments,
                    commands,
                    options,
                    tools,
                    stored_hash,
                }))
            }

            fn visit_map<V>(self, mut map: V) -> StdResult<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut environment_tag = None;
                let mut commands = None;
                let mut options = None;
                let mut tools = None;
                let mut stored_hash = None;
                self.0.push(Vec::new());
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Environments => {
                            if environment_tag.is_some() {
                                return Err(Error::duplicate_field("environments"));
                            }
                            environment_tag =
                                Some(map.next_value_seed(ReadWriteEnvironmentSequenceSeed(self.0))?);
                        }
                        Field::Commands => {
                            if commands.is_some() {
                                return Err(Error::duplicate_field("commands"));
                            }
                            commands = Some(map.next_value_seed(CommandSequenceSeed(self.0))?);
                        }
                        Field::Options => {
                            if options.is_some() {
                                return Err(Error::duplicate_field("options"));
                            }
                            options = Some(map.next_value::<Option<Environment>>()?);
                        }
                        Field::Tools => {
                            if tools.is_some() {
                                return Err(Error::duplicate_field("tools"));
                            }
                            tools = Some(map.next_value::<Vec<Node>>()?);
                        }
                        Field::StoredHash => {
                            if stored_hash.is_some() {
                                return Err(Error::duplicate_field("stored_hash"));
                            }
                            stored_hash = Some(map.next_value()?);
                        }
                    }
                }
                let environments = self.0.pop().unwrap();
                environment_tag.ok_or_else(|| Error::missing_field("environments"))?;
                let commands = commands.ok_or_else(|| Error::missing_field("commands"))?;
                let tools = tools.ok_or_else(|| Error::missing_field("tools"))?;
                let options = options.ok_or_else(|| Error::missing_field("options"))?;
                let stored_hash =
                    stored_hash.ok_or_else(|| Error::missing_field("stored_hash"))?;
                Ok(Some(CommandOutput {
                    environments,
                    commands,
                    options,
                    tools,
                    stored_hash,
                }))
            }
        }

        deserializer.deserialize_option(
            CommandOutputVisitor(self.0),
        )
    }
}

#[derive(Serialize, Deserialize)]
pub(crate) struct CommandHash {
    pub(crate) file_dependencies: Vec<PathBuf>,
    pub(crate) option_dependencies: Vec<String>,
    pub(crate) variable_dependencies: Vec<Vec<String>>,
    pub(crate) glob_dependencies: Vec<(Node, String, SerializedHash)>,
    pub(crate) hash: Option<(SerializedHash, SerializedHash, SerializedHash, SerializedHash)>,
}

pub(crate) struct SerializedHash(pub Hash);

impl Serialize for SerializedHash {
    fn serialize<S>(&self, serializer: S) -> StdResult<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(self.0.to_hex().as_str())
    }
}

impl<'de> Deserialize<'de> for SerializedHash {
    fn deserialize<D>(deserializer: D) -> StdResult<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct HashVisitor;

        impl<'de> Visitor<'de> for HashVisitor {
            type Value = SerializedHash;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("a byte string")
            }

            fn visit_str<E>(self, v: &str) -> StdResult<Self::Value, E>
            where
                E: Error,
            {
                Ok(SerializedHash(Hash::from_hex(v).map_err(|x| Error::custom(x))?))
            }

            fn visit_string<E>(self, v: String) -> StdResult<Self::Value, E>
            where
                E: Error,
            {
                Ok(SerializedHash(Hash::from_hex(v).map_err(|x| Error::custom(x))?))
            }
        }

        deserializer.deserialize_string(HashVisitor)
    }
}
