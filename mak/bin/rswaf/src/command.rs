use crate::environment::{
    Environment, EnvironmentSeed, EnvironmentSequenceSeed, SerializedEnvironment,
};
use crate::error::{MakeError, Result};
use crate::log::Logger;
use crate::node::Node;
use crate::options::{CommandLineParser, Options};
use crate::context::Context;
use blake3::{Hash, Hasher};
use mlua::{Lua, Table};
use serde::de::{DeserializeSeed, Error, MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use serde::ser::SerializeStruct;
use std::collections::HashMap;
use std::fmt;
use std::iter::zip;
use std::mem::swap;
use std::ops::{Deref, DerefMut};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

use mlua::Error as LuaError;
use mlua::Value as LuaValue;
use std::result::Result as StdResult;


#[derive(Serialize)]
pub(crate) struct Command {
    pub(crate) spec: CommandSpec,
    pub(crate) output: Option<CommandOutput>,
    #[serde(skip_serializing)]
    pub(crate) up_to_date: bool,
}

impl Command {
    pub(crate) fn init() -> Result<Self> {
        let init_command = Command {
            spec: CommandSpec::create_init(),
            output: None,
            up_to_date: false,
        };
        Ok(init_command)
    }

    pub(crate) fn run_with_deps<Iter>(
        &mut self,
        mut path: Iter,
        envs: &Vec<Arc<Mutex<Environment>>>,
        options: Arc<Mutex<Environment>>,
        command_line: Arc<Mutex<CommandLineParser>>,
        mut current_path: Vec<String>,
        registered_commands: &mut HashMap<String, Vec<String>>,
        mut logger: Logger,
        log_why: bool,
        run_implicit: bool,
    ) -> Result<Logger>
    where
        Iter: Iterator,
        <Iter as Iterator>::Item: PartialEq<String>,
        <Iter as Iterator>::Item: fmt::Display,
    {
        current_path.push(self.spec.name.clone());
        let next_item = path.next();

        if !self.up_to_date {
            let options = if run_implicit || next_item.is_some() {
                if let Some(output) = &self.output {
                    if let Some(options) = &output.options {
                        let options = options.clone();
                        command_line
                            .lock()
                            .unwrap()
                            .parse_command_line_into(options.lock().unwrap().deref_mut());

                        options
                    } else { options.clone() }
                } else { options.clone() }
            } else { options.clone() };

            let do_run = if let Some(output) = &mut self.output {
                if let Some(stored_hash) = &output.stored_hash.hash {
                    let hash_result = output.hash(&Some(options.clone()), envs);
                    if let Ok(hash) = hash_result {
                        if !hash.0.0.eq(&stored_hash.0.0) {
                            if log_why {
                                logger.debug(
                                    format!(
                                        "evaluating command `{}` because files have changed on disc",
                                        self.spec.name
                                    ).as_str(),
                                );
                            }
                            true
                        } else if !hash.1.0.eq(&stored_hash.1.0) {
                            if log_why {
                                logger.debug(
                                    format!(
                                        "evaluating command `{}` because command-line options have changed",
                                        self.spec.name
                                    ).as_str(),
                                );
                            }
                            true
                        } else if !hash.2.0.eq(&stored_hash.2.0) {
                            if log_why {
                                logger.debug(
                                    format!(
                                        "evaluating command `{}` because the environment has changed",
                                        self.spec.name
                                    ).as_str(),
                                );
                            }
                            true
                        } else {
                            let mut pattern_changed = false;
                            for (path, pattern, hash) in &output.stored_hash.glob_dependencies {
                                if !path.is_dir() {
                                    logger.debug(
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
                                        if log_why {
                                            logger.debug(
                                                format!(
                                                    "evaluating command `{}` because the result of file search `{}/{}` has changed.",
                                                    self.spec.name,
                                                    path.path().to_string_lossy(),
                                                    pattern
                                                ).as_str(),
                                            );
                                        }
                                        pattern_changed = true;
                                        break;
                                    }
                                }
                            }
                            pattern_changed
                        }
                    } else {
                        if log_why {
                            logger.debug(
                                format!(
                                    "evaluating command `{}` because the hash could not be computed",
                                    self.spec.name
                                ).as_str(),
                            );
                        }
                        true
                    }
                } else {
                    if log_why {
                        logger.debug(
                            format!(
                                "evaluating command `{}` because the hash does not exist",
                                self.spec.name
                            ).as_str(),
                        );
                    }
                    true
                }
            } else {
                if log_why {
                    logger.debug(
                        format!(
                            "evaluating command `{}` because the command was never run",
                            self.spec.name
                        ).as_str(),
                    );
                }
                true
            };

            if do_run {
                logger = self.run(
                    Options::from_env(options),
                    envs,
                    current_path.clone(),
                    registered_commands,
                    logger,
                )?;
            } else {
                self.up_to_date = true;
                if next_item.is_none() {
                    logger.debug(format!("`{}` is up-to-date", self.spec.name).as_str());
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
                            options,
                            command_line,
                            current_path,
                            registered_commands,
                            logger,
                            log_why,
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
        struct CommandCacheSeed(Vec<Vec<Arc<Mutex<Environment>>>>);

        impl<'de> DeserializeSeed<'de> for CommandCacheSeed {
            type Value = Vec<Command>;

            fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
            where
                D: Deserializer<'de>,
            {
                struct CommandCacheVisitor(Vec<Vec<Arc<Mutex<Environment>>>>);

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
        self.spec = cached_spec;
        path.push(self.spec.name.clone());
        if self.output.is_none() {
            self.output = cached_output;
        } else if let Some(cached_output) = cached_output {
            let output = self.output.as_mut().unwrap();
            output.environments = cached_output.environments;
            output.options = cached_output.options;
            output.stored_hash = cached_output.stored_hash;

            let mut old_commands = Vec::new();
            swap(&mut output.commands, &mut old_commands);

            for new_cmd in cached_output.commands {
                if let Some(index) = old_commands
                    .iter()
                    .position(|x| x.spec.name.eq(&new_cmd.spec.name))
                {
                    let mut old_cmd = old_commands.swap_remove(index);
                    old_cmd.merge_with(new_cmd.spec, new_cmd.output, command_map, path);
                    output.commands.push(old_cmd);
                } else {
                    new_cmd.register(command_map, path);
                    output.commands.push(new_cmd);
                }
            }
            output.commands.append(&mut old_commands);
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
        envs: &Vec<Arc<Mutex<Environment>>>,
        command_path: Vec<String>,
        commands: &mut HashMap<String, Vec<String>>,
        logger: Logger,
    ) -> Result<Logger> {
        let current_dir = std::env::current_dir().unwrap();
        let bld_dir = if let Options::Environment(options) = &options_context {
            options.lock().unwrap().get_raw("out").as_node()?
        } else {
            Node::from(&current_dir)
        };
        commands.retain(|_, v| !v.starts_with(command_path.as_slice()));
        bld_dir.mkdir()?;
        let run_envs: Vec<Arc<Mutex<Environment>>> = self
            .spec
            .envs
            .iter()
            .enumerate()
            .map(|(i, &x)| Arc::new(Mutex::new(Environment::derive_from_parent(&envs[x], i))))
            .collect();
        let start_env = run_envs[0].clone();
        let mut cmd = Context {
            spec: self.spec.clone(),
            output: CommandOutput {
                environments: run_envs,
                options: match &options_context {
                    Options::CommandLineParser(_) => None,
                    Options::Environment(e) => Some(e.clone()),
                },
                commands: Vec::new(),
                stored_hash: CommandHash {
                    file_dependencies: Vec::new(),
                    option_dependencies: Vec::new(),
                    variable_dependencies: Vec::new(),
                    glob_dependencies: Vec::new(),
                    hash: None,
                },
            },
            environment: start_env,
            path: Node::from(&current_dir),
            src_dir: Node::from(&current_dir),
            bld_dir,
            options: options_context,
            logger,
            command_path,
            commands: commands.clone(),
        };

        {
            let lua = Lua::new();
            let chunk = lua.load(Path::new(ROOT_SCRIPT));
            let globals = lua.globals();
            {
                lua.scope(|scope| chunk.call(scope.create_userdata_ref_mut(&mut cmd).unwrap()))
                    .map_err(|err| match err {
                        LuaError::ExternalError(_) => MakeError {
                            location: None,
                            message: String::from(std::format!(
                                "could not find root script {}.",
                                ROOT_SCRIPT
                            )),
                        },
                        _ => MakeError::from(err),
                    })?;
            }

            /* retrieve a list of modules */
            let package: Table = globals.get("package")?;
            let package_path: String = package.get("path")?;
            let packages: Table = package.get("loaded")?;
            packages.for_each(|key: String, _: LuaValue| {
                for path in package_path.split(';') {
                    let module_path = path.replace("?", key.replace(".", "/").as_str());

                    if Path::new(module_path.as_str()).is_file() {
                        cmd.output
                            .stored_hash
                            .file_dependencies
                            .push(PathBuf::from(module_path));
                        break;
                    }
                }
                Ok(())
            })?;
            for env in envs {
                cmd.output.stored_hash.variable_dependencies.push(
                    env.lock()
                        .unwrap()
                        .used_keys
                        .iter()
                        .map(|x| x.clone())
                        .collect(),
                )
            }
            if let Some(options_env) = &cmd.output.options {
                cmd.output.stored_hash.option_dependencies = options_env
                    .lock()
                    .unwrap()
                    .used_keys
                    .iter()
                    .map(|x| x.clone())
                    .collect();
            }
            cmd.output.stored_hash.hash = Some(cmd.output.hash(&cmd.output.options, envs)?);
        }
        *commands = cmd.commands;
        self.merge_with(cmd.spec, Some(cmd.output), commands, &mut cmd.command_path);

        self.up_to_date = true;
        Ok(cmd.logger)
    }
}

pub(crate) struct CommandSeed<'a>(pub &'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

impl<'de, 'a> DeserializeSeed<'de> for CommandSeed<'a> {
    type Value = Command;

    fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Spec,
            Output,
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
                        formatter.write_str("`spec` or `output`")
                    }

                    fn visit_str<E>(self, value: &str) -> StdResult<Field, E>
                    where
                        E: Error,
                    {
                        match value {
                            "spec" => Ok(Field::Spec),
                            "output" => Ok(Field::Output),
                            _ => Err(Error::unknown_field(value, &["spec", "output"])),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct CommandVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

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
                Ok(Command {
                    spec,
                    output,
                    up_to_date: false,
                })
            }

            fn visit_map<V>(self, mut map: V) -> StdResult<Command, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut spec = None;
                let mut output = None;
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
                    }
                }
                let spec = spec.ok_or_else(|| Error::missing_field("spec"))?;
                let output = output.ok_or_else(|| Error::missing_field("output"))?;
                Ok(Command {
                    spec,
                    output,
                    up_to_date: false,
                })
            }
        }

        deserializer.deserialize_struct("Command", &["spec", "output"], CommandVisitor(self.0))
    }
}

struct CommandSequenceSeed<'a>(&'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

impl<'de, 'a> DeserializeSeed<'de> for CommandSequenceSeed<'a> {
    type Value = Vec<Command>;

    fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct CommandSequenceVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

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
    /* the name of the command. Must be unique */
    pub(crate) name: String,
    /* the name of the context in Lua. Usually a prefix of the command. */
    pub(crate) function: String,
    /* the index/id of the environment. Commands create and save environments when they run.
    The combination command/ID allows to retrieve an environment. */
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
    pub(crate) environments: Vec<Arc<Mutex<Environment>>>,
    pub(crate) commands: Vec<Command>,
    pub(crate) options: Option<Arc<Mutex<Environment>>>,
    pub(crate) stored_hash: CommandHash,
}

impl CommandOutput {
    fn hash(
        &self,
        options: &Option<Arc<Mutex<Environment>>>,
        envs: &Vec<Arc<Mutex<Environment>>>,
    ) -> std::io::Result<(SerializedHash, SerializedHash, SerializedHash)> {
        let mut hasher = blake3::Hasher::new();
        for file in &self.stored_hash.file_dependencies {
            hasher.update(file.as_os_str().as_encoded_bytes());
            hasher.update_reader(std::fs::File::open(file)?)?;
        }
        let hash1 = SerializedHash(hasher.finalize());
        hasher = blake3::Hasher::new();
        if let Some(options_env_arc) = options {
            let options_env = options_env_arc.lock().unwrap();
            for env_var in &self.stored_hash.option_dependencies {
                options_env.get_raw(env_var.as_str()).hash(&mut hasher);
            }
        }
        let hash2 = SerializedHash(hasher.finalize());
        hasher = blake3::Hasher::new();
        for (vars, env_arc) in zip(self.stored_hash.variable_dependencies.iter(), envs.iter()) {
            let env = env_arc.lock().unwrap();
            for var in vars {
                env.get_raw(var.as_str()).hash(&mut hasher);
            }
        }
        let hash3 = SerializedHash(hasher.finalize());
        Ok((hash1, hash2, hash3))
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
                .map(|v| SerializedEnvironment(v))
                .collect::<Vec<SerializedEnvironment>>(),
        )?;
        s.serialize_field("commands", &self.commands)?;
        if let Some(options) = &self.options {
            s.serialize_field("options", &Some(SerializedEnvironment(&options)))?;
        }
        s.serialize_field("stored_hash", &self.stored_hash)?;
        s.end()
    }
}

struct CommandOutputSeed<'a>(&'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

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

        struct CommandOutputVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

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
                    &["environments", "commands", "options", "stored_hash"],
                    self,
                )
            }

            fn visit_seq<V>(self, mut seq: V) -> StdResult<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                (*self.0).push(Vec::new());
                seq.next_element_seed(EnvironmentSequenceSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let commands = seq
                    .next_element_seed(CommandSequenceSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(1, &self))?;
                let options = seq
                    .next_element_seed(EnvironmentSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(2, &self))?;
                let stored_hash = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(3, &self))?;
                let environments = self.0.pop().unwrap();
                Ok(Some(CommandOutput {
                    environments,
                    commands,
                    options: Some(options),
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
                let mut stored_hash = None;
                self.0.push(Vec::new());
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Environments => {
                            if environment_tag.is_some() {
                                return Err(Error::duplicate_field("environments"));
                            }
                            environment_tag =
                                Some(map.next_value_seed(EnvironmentSequenceSeed(self.0))?);
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
                            options = Some(map.next_value_seed(EnvironmentSeed(self.0))?);
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
                let stored_hash =
                    stored_hash.ok_or_else(|| Error::missing_field("stored_hash"))?;
                Ok(Some(CommandOutput {
                    environments,
                    commands,
                    options,
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
    pub(crate) hash: Option<(SerializedHash, SerializedHash, SerializedHash)>,
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

const ROOT_SCRIPT: &str = "make.lua";
