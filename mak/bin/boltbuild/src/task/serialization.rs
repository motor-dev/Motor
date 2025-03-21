use super::{Task, TaskSeed};
use crate::environment::serialization::{OverlayMapSeed, OverlayMapVec, SerializedOverlayMap};
use crate::node::Node;
use serde::de::{DeserializeSeed, Error, MapAccess, SeqAccess, Visitor};
use serde::ser::SerializeStruct;
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::fmt;

impl Serialize for Task {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut s = serializer.serialize_struct("Task", 9)?;
        s.serialize_field("driver", &self.driver)?;
        s.serialize_field("generator", &self.generator)?;
        s.serialize_field("group", &self.group)?;
        s.serialize_field("env", &SerializedOverlayMap(&self.env))?;
        s.serialize_field("inputs", &self.inputs)?;
        s.serialize_field("outputs", &self.outputs)?;
        s.serialize_field("predecessors", &self.predecessors)?;
        s.serialize_field("successors", &self.successors)?;
        s.serialize_field("signature", &self.signature)?;
        s.end()
    }
}

impl<'de, 'a> DeserializeSeed<'de> for TaskSeed<'a> {
    type Value = Task;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Driver,
            Generator,
            Group,
            Env,
            Inputs,
            Outputs,
            Predecessors,
            Successors,
            Signature,
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
                            .write_str("`driver`, `generator`, `group`, `env`, `inputs`, `outputs`, `predecessors`, `successors` or `signature`")
                    }

                    fn visit_str<E>(self, value: &str) -> Result<Field, E>
                    where
                        E: Error,
                    {
                        match value {
                            "driver" => Ok(Field::Driver),
                            "generator" => Ok(Field::Generator),
                            "group" => Ok(Field::Group),
                            "env" => Ok(Field::Env),
                            "inputs" => Ok(Field::Inputs),
                            "outputs" => Ok(Field::Outputs),
                            "predecessors" => Ok(Field::Predecessors),
                            "successors" => Ok(Field::Successors),
                            "signature" => Ok(Field::Signature),
                            _ => Err(Error::unknown_field(
                                value,
                                &[
                                    "driver",
                                    "generator",
                                    "group",
                                    "env",
                                    "inputs",
                                    "outputs",
                                    "predecessors",
                                    "successors",
                                    "signature",
                                ],
                            )),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct TaskVisitor<'a>(&'a mut OverlayMapVec);

        impl<'de, 'a> Visitor<'de> for TaskVisitor<'a> {
            type Value = Task;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct Task")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let driver = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let generator = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(1, &self))?;
                let group = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(2, &self))?;
                let env = seq
                    .next_element_seed(OverlayMapSeed {
                        current: &mut Vec::new(),
                        parent: self.0,
                        index: 0,
                    })?
                    .ok_or_else(|| Error::invalid_length(3, &self))?;
                let inputs = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(4, &self))?;
                let outputs = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(5, &self))?;
                let predecessors = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(6, &self))?;
                let successors = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(7, &self))?;
                let signature = seq
                    .next_element()?
                    .ok_or_else(|| Error::invalid_length(8, &self))?;
                Ok(Task {
                    driver,
                    generator,
                    group,
                    env,
                    inputs,
                    outputs,
                    predecessors,
                    successors,
                    signature,
                })
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut driver = None;
                let mut generator = None;
                let mut group = None;
                let mut env = None;
                let mut inputs = None;
                let mut outputs = None;
                let mut predecessors = None;
                let mut successors = None;
                let mut signature = None;
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Driver => {
                            if driver.is_some() {
                                return Err(Error::duplicate_field("driver"));
                            }
                            driver = Some(map.next_value()?);
                        }
                        Field::Generator => {
                            if generator.is_some() {
                                return Err(Error::duplicate_field("generator"));
                            }
                            generator = Some(map.next_value()?);
                        }
                        Field::Group => {
                            if group.is_some() {
                                return Err(Error::duplicate_field("group"));
                            }
                            group = Some(map.next_value()?);
                        }
                        Field::Env => {
                            if env.is_some() {
                                return Err(Error::duplicate_field("env"));
                            }
                            env = Some(map.next_value_seed(OverlayMapSeed {
                                current: &mut Vec::new(),
                                parent: self.0,
                                index: 0,
                            })?);
                        }
                        Field::Inputs => {
                            if inputs.is_some() {
                                return Err(Error::duplicate_field("inputs"));
                            }
                            inputs = Some(map.next_value::<Vec<Node>>()?);
                        }
                        Field::Outputs => {
                            if outputs.is_some() {
                                return Err(Error::duplicate_field("outputs"));
                            }
                            outputs = Some(map.next_value()?);
                        }
                        Field::Predecessors => {
                            if predecessors.is_some() {
                                return Err(Error::duplicate_field("predecessors"));
                            }
                            predecessors = Some(map.next_value()?);
                        }
                        Field::Successors => {
                            if successors.is_some() {
                                return Err(Error::duplicate_field("successors"));
                            }
                            successors = Some(map.next_value()?);
                        }
                        Field::Signature => {
                            if signature.is_some() {
                                return Err(Error::duplicate_field("signature"));
                            }
                            signature = Some(map.next_value()?);
                        }
                    }
                }
                let driver = driver.ok_or_else(|| Error::missing_field("driver"))?;
                let generator = generator.ok_or_else(|| Error::missing_field("generator"))?;
                let group = group.ok_or_else(|| Error::missing_field("group"))?;
                let env = env.ok_or_else(|| Error::missing_field("env"))?;
                let inputs = inputs.ok_or_else(|| Error::missing_field("inputs"))?;
                let outputs = outputs.ok_or_else(|| Error::missing_field("outputs"))?;
                let predecessors =
                    predecessors.ok_or_else(|| Error::missing_field("predecessors"))?;
                let successors = successors.ok_or_else(|| Error::missing_field("successors"))?;
                let signature = signature.ok_or_else(|| Error::missing_field("signature"))?;
                Ok(Task {
                    driver,
                    generator,
                    group,
                    env,
                    inputs,
                    outputs,
                    predecessors,
                    successors,
                    signature,
                })
            }
        }

        deserializer.deserialize_struct(
            "Task",
            &[
                "driver",
                "generator",
                "group",
                "env",
                "inputs",
                "outputs",
                "predecessors",
                "successors",
                "signature",
            ],
            TaskVisitor(self.0),
        )
    }
}
