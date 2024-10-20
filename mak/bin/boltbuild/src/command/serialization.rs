use super::{Command, CommandOutput, CommandStatus, SerializedHash, TaskSeq};
use crate::environment::{Environment, ReadWriteEnvironmentVec, ReadWriteEnvironmentSequenceSeed, SerializedReadWriteEnvironment};
use crate::node::Node;
use crate::task::{Task, TaskSeed};

use std::collections::HashMap;
use std::fmt;
use std::path::PathBuf;
use blake3::Hash;
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use serde::de::{DeserializeSeed, Error, MapAccess, SeqAccess, Visitor};
use serde::ser::SerializeStruct;

impl Command {
    pub(crate) fn load_from_file(
        &mut self,
        file: std::fs::File,
        command_map: &mut HashMap<String, Vec<String>>,
    ) -> crate::error::Result<()> {
        struct CommandCacheSeed<'a>(&'a ReadWriteEnvironmentVec);

        impl<'de, 'a> DeserializeSeed<'de> for CommandCacheSeed<'a> {
            type Value = Vec<Command>;

            fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
            where
                D: Deserializer<'de>,
            {
                struct CommandCacheVisitor<'a>(&'a ReadWriteEnvironmentVec);

                impl<'de, 'a> Visitor<'de> for CommandCacheVisitor<'a> {
                    type Value = Vec<Command>;

                    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                        formatter.write_str("sequence of Command")
                    }

                    fn visit_seq<V>(self, mut seq: V) -> Result<Vec<Command>, V::Error>
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

                deserializer.deserialize_seq(CommandCacheVisitor(self.0))
            }
        }

        let output = self.output.as_ref().unwrap();
        let reader = std::io::BufReader::new(file);
        let commands = CommandCacheSeed(&output.environments)
            .deserialize(&mut serde_json::Deserializer::from_reader(reader))?;
        self.merge_cache(commands, command_map);
        Ok(())
    }

    pub(crate) fn save_to_file(&self, file: std::fs::File) -> crate::error::Result<()> {
        Ok(serde_json::to_writer_pretty(
            file,
            &self.output.as_ref().unwrap().commands,
        )?)
    }
}


pub(crate) struct CommandSeed<'a>(pub &'a ReadWriteEnvironmentVec);

impl<'de, 'a> DeserializeSeed<'de> for CommandSeed<'a> {
    type Value = Command;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Spec,
            Output,
            Status,
        }

        impl<'de> Deserialize<'de> for Field {
            fn deserialize<D>(deserializer: D) -> Result<Field, D::Error>
            where
                D: Deserializer<'de>,
            {
                struct FieldVisitor;

                impl<'de> Visitor<'de> for FieldVisitor {
                    type Value = Field;

                    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                        formatter.write_str("`spec`, `output` or `status`")
                    }

                    fn visit_str<E>(self, value: &str) -> Result<Field, E>
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

        struct CommandVisitor<'a>(&'a ReadWriteEnvironmentVec);

        impl<'de, 'a> Visitor<'de> for CommandVisitor<'a> {
            type Value = Command;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct Command")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Command, V::Error>
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

            fn visit_map<V>(self, mut map: V) -> Result<Command, V::Error>
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

struct CommandSequenceSeed<'a>(&'a ReadWriteEnvironmentVec);

impl<'de, 'a> DeserializeSeed<'de> for CommandSequenceSeed<'a> {
    type Value = Vec<Command>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct CommandSequenceVisitor<'a>(&'a ReadWriteEnvironmentVec);

        impl<'de, 'a> Visitor<'de> for CommandSequenceVisitor<'a> {
            type Value = Vec<Command>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("sequence of Command")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Vec<Command>, V::Error>
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

impl Serialize for CommandOutput {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut s = serializer.serialize_struct("Command", 7)?;
        s.serialize_field(
            "environments",
            &self
                .environments
                .iter()
                .map(SerializedReadWriteEnvironment)
                .collect::<Vec<SerializedReadWriteEnvironment>>(),
        )?;
        s.serialize_field("commands", &self.commands)?;
        s.serialize_field("options", &self.options)?;
        s.serialize_field("tools", &self.tools)?;
        s.serialize_field("stored_hash", &self.stored_hash)?;
        s.serialize_field("groups", &self.groups)?;

        let tasks = match &self.tasks {
            TaskSeq::None => None,
            TaskSeq::Cached(cache_file) => Some(cache_file),
            TaskSeq::List(_) => return Err(serde::ser::Error::custom("Task list should be serialized in a separate cache")),
        };
        s.serialize_field("tasks", &tasks)?;
        s.end()
    }
}

struct CommandOutputSeed<'a>(&'a ReadWriteEnvironmentVec);

impl<'de, 'a> DeserializeSeed<'de> for CommandOutputSeed<'a> {
    type Value = Option<CommandOutput>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Environments,
            Commands,
            Options,
            Tools,
            StoredHash,
            Groups,
            Tasks,
        }

        impl<'de> Deserialize<'de> for Field {
            fn deserialize<D>(deserializer: D) -> Result<Field, D::Error>
            where
                D: Deserializer<'de>,
            {
                struct FieldVisitor;

                impl<'de> Visitor<'de> for FieldVisitor {
                    type Value = Field;

                    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                        formatter
                            .write_str("`environments`, `commands`, `options`, `tools`, `stored_hash`, `groups` or `tasks`")
                    }

                    fn visit_str<E>(self, value: &str) -> Result<Field, E>
                    where
                        E: Error,
                    {
                        match value {
                            "environments" => Ok(Field::Environments),
                            "commands" => Ok(Field::Commands),
                            "options" => Ok(Field::Options),
                            "tools" => Ok(Field::Tools),
                            "stored_hash" => Ok(Field::StoredHash),
                            "groups" => Ok(Field::Groups),
                            "tasks" => Ok(Field::Tasks),
                            _ => Err(Error::unknown_field(
                                value,
                                &["environments", "commands", "options", "tools", "stored_hash", "groups", "tasks"],
                            )),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct CommandOutputVisitor<'a>(&'a ReadWriteEnvironmentVec);

        impl<'de, 'a> Visitor<'de> for CommandOutputVisitor<'a> {
            type Value = Option<CommandOutput>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct CommandOutput")
            }

            fn visit_none<E>(self) -> Result<Self::Value, E>
            where
                E: Error,
            {
                Ok(None)
            }

            fn visit_some<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
            where
                D: Deserializer<'de>,
            {
                deserializer.deserialize_struct(
                    "Command",
                    &["environments", "commands", "options", "tools", "stored_hash", "groups", "tasks"],
                    self,
                )
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let environments = seq.next_element_seed(ReadWriteEnvironmentSequenceSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let commands = seq
                    .next_element_seed(CommandSequenceSeed(&environments))?
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
                let groups = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(5, &self))?;
                let tasks = seq
                    .next_element::<Option<PathBuf>>()?
                    .ok_or_else(|| Error::invalid_length(6, &self))?;
                Ok(Some(CommandOutput {
                    environments,
                    commands,
                    options,
                    tools,
                    stored_hash,
                    groups,
                    tasks: match tasks {
                        None => TaskSeq::None,
                        Some(path) => TaskSeq::Cached(path)
                    },
                }))
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut environments = None;
                let mut commands = None;
                let mut options = None;
                let mut tools = None;
                let mut stored_hash = None;
                let mut groups = None;
                let mut tasks = None;
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Environments => {
                            if environments.is_some() {
                                return Err(Error::duplicate_field("environments"));
                            }
                            environments = Some(map.next_value_seed(ReadWriteEnvironmentSequenceSeed(self.0))?);
                        }
                        Field::Commands => {
                            if commands.is_some() {
                                return Err(Error::duplicate_field("commands"));
                            }
                            if environments.is_none() {
                                return Err(Error::custom("environments must be defined before the commands that use them"));
                            }
                            commands = Some(map.next_value_seed(CommandSequenceSeed(environments.as_ref().unwrap()))?);
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
                        Field::Groups => {
                            if groups.is_some() {
                                return Err(Error::duplicate_field("groups"));
                            }
                            groups = Some(map.next_value()?);
                        }
                        Field::Tasks => {
                            if tasks.is_some() {
                                return Err(Error::duplicate_field("tasks"));
                            }
                            tasks = Some(map.next_value::<Option<PathBuf>>()?);
                        }
                    }
                }
                let environments = environments.ok_or_else(|| Error::missing_field("environments"))?;
                let commands = commands.ok_or_else(|| Error::missing_field("commands"))?;
                let tools = tools.ok_or_else(|| Error::missing_field("tools"))?;
                let options = options.ok_or_else(|| Error::missing_field("options"))?;
                let stored_hash = stored_hash.ok_or_else(|| Error::missing_field("stored_hash"))?;
                let groups = groups.ok_or_else(|| Error::missing_field("groups"))?;
                let tasks = tasks.ok_or_else(|| Error::missing_field("tasks"))?;
                Ok(Some(CommandOutput {
                    environments,
                    commands,
                    options,
                    tools,
                    stored_hash,
                    groups,
                    tasks: match tasks {
                        None => TaskSeq::None,
                        Some(path) => TaskSeq::Cached(path),
                    },
                }))
            }
        }

        deserializer.deserialize_option(
            CommandOutputVisitor(self.0),
        )
    }
}

impl Serialize for SerializedHash {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(self.0.to_hex().as_str())
    }
}

impl<'de> Deserialize<'de> for SerializedHash {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct HashVisitor;

        impl<'de> Visitor<'de> for HashVisitor {
            type Value = SerializedHash;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("a byte string")
            }

            fn visit_str<E>(self, v: &str) -> Result<Self::Value, E>
            where
                E: Error,
            {
                Ok(SerializedHash(Hash::from_hex(v).map_err(|x| Error::custom(x))?))
            }

            fn visit_string<E>(self, v: String) -> Result<Self::Value, E>
            where
                E: Error,
            {
                Ok(SerializedHash(Hash::from_hex(v).map_err(|x| Error::custom(x))?))
            }
        }

        deserializer.deserialize_string(HashVisitor)
    }
}

pub(super) struct TaskSequenceSeed<'a>(pub &'a ReadWriteEnvironmentVec);

impl<'de, 'a> DeserializeSeed<'de> for TaskSequenceSeed<'a> {
    type Value = Vec<Task>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct TaskSequenceVisitor<'a>(&'a ReadWriteEnvironmentVec);

        impl<'de, 'a> Visitor<'de> for TaskSequenceVisitor<'a> {
            type Value = Vec<Task>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("sequence of Task")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let mut result = Vec::new();
                if let Some(size_hint) = seq.size_hint() {
                    result.reserve(size_hint);
                }
                while let Some(elem) = seq.next_element_seed(TaskSeed(self.0))? {
                    result.push(elem);
                }
                Ok(result)
            }
        }

        deserializer.deserialize_seq(TaskSequenceVisitor(self.0))
    }
}
