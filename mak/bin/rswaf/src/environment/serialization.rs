use super::{Environment, SerializedReadWriteEnvironment, ReadWriteEnvironment, ReadWriteEnvironmentSequenceSeed};
use super::environment::EnvironmentParent;

use std::collections::{BTreeMap, HashSet};
use std::fmt;
use std::sync::{Arc, Mutex};

use serde::{de, Deserialize, Deserializer, Serialize, Serializer};
use serde::de::{DeserializeSeed, MapAccess, SeqAccess, Visitor};
use serde::ser::SerializeStruct;


impl<'a> Serialize for SerializedReadWriteEnvironment<'a> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut s = serializer.serialize_struct("Environment", 2)?;
        s.serialize_field(
            "parent",
            &match &self.0.lock().unwrap().parent {
                EnvironmentParent::None => SerializedEnvironmentParent::None,
                EnvironmentParent::Current(p) => {
                    SerializedEnvironmentParent::Current(p.lock().unwrap().index)
                }
                EnvironmentParent::Parent(p) => {
                    SerializedEnvironmentParent::Parent(p.lock().unwrap().index)
                }
            },
        )?;
        s.serialize_field("values", &self.0.lock().unwrap().environment.values.iter().collect::<BTreeMap<_, _>>())?;
        s.end()
    }
}

pub(crate) struct ReadWriteEnvironmentSeed<'a>(pub &'a Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

#[derive(Serialize, Deserialize)]
enum SerializedEnvironmentParent {
    None,
    Current(usize),
    Parent(usize),
}

impl<'de, 'a> DeserializeSeed<'de> for ReadWriteEnvironmentSeed<'a> {
    type Value = Arc<Mutex<ReadWriteEnvironment>>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Parent,
            Values,
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
                        formatter.write_str("`parent`, or `values`")
                    }

                    fn visit_str<E>(self, value: &str) -> Result<Field, E>
                    where
                        E: de::Error,
                    {
                        match value {
                            "parent" => Ok(Field::Parent),
                            "values" => Ok(Field::Values),
                            _ => Err(de::Error::unknown_field(value, &["parent", "values"])),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct ReadWriteEnvironmentVisitor<'a>(&'a Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

        impl<'de, 'a> Visitor<'de> for ReadWriteEnvironmentVisitor<'a> {
            type Value = Arc<Mutex<ReadWriteEnvironment>>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct Environment")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let parent = seq
                    .next_element::<SerializedEnvironmentParent>()?
                    .ok_or_else(|| de::Error::invalid_length(0, &self))?;
                let values = seq
                    .next_element()?
                    .ok_or_else(|| de::Error::invalid_length(1, &self))?;
                let parent = match parent {
                    SerializedEnvironmentParent::None => EnvironmentParent::None,
                    SerializedEnvironmentParent::Current(index) => {
                        let environments = self.0.last().unwrap();
                        if environments.len() <= index {
                            return Err(de::Error::custom(format!("invalid environment index {}; expected an index in the range 0..{}", index, environments.len())));
                        }
                        EnvironmentParent::Current(environments[index].clone())
                    }
                    SerializedEnvironmentParent::Parent(index) => {
                        let environments = &self.0[self.0.len() - 2];
                        if environments.len() <= index {
                            return Err(de::Error::custom(format!("invalid environment index {}; expected an index in the range 0..{}", index, environments.len())));
                        }
                        EnvironmentParent::Parent(environments[index].clone())
                    }
                };
                Ok(Arc::new(Mutex::new(ReadWriteEnvironment {
                    parent,
                    index: self.0.last().unwrap().len(),
                    environment: Environment {
                        values,
                        used_keys: HashSet::new(),
                    },
                })))
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut parent = None;
                let mut values = None;
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Parent => {
                            if parent.is_some() {
                                return Err(de::Error::duplicate_field("parent"));
                            }
                            parent = Some(map.next_value()?);
                        }
                        Field::Values => {
                            if values.is_some() {
                                return Err(de::Error::duplicate_field("values"));
                            }
                            values = Some(map.next_value()?);
                        }
                    }
                }
                let parent = parent.ok_or_else(|| de::Error::missing_field("parent"))?;
                let parent = match parent {
                    SerializedEnvironmentParent::None => EnvironmentParent::None,
                    SerializedEnvironmentParent::Current(index) => {
                        let environments = self.0.last().unwrap();
                        if environments.len() <= index {
                            return Err(de::Error::custom(format!("invalid environment index {}; expected an index in the range 0..{}", index, environments.len())));
                        }
                        EnvironmentParent::Current(environments[index].clone())
                    }
                    SerializedEnvironmentParent::Parent(index) => {
                        let environments = &self.0[self.0.len() - 2];
                        if environments.len() <= index {
                            return Err(de::Error::custom(format!("invalid environment index {}; expected an index in the range 0..{}", index, environments.len())));
                        }
                        EnvironmentParent::Parent(environments[index].clone())
                    }
                };
                let values = values.ok_or_else(|| de::Error::missing_field("values"))?;
                Ok(Arc::new(Mutex::new(ReadWriteEnvironment {
                    parent,
                    index: self.0.last().unwrap().len(),
                    environment: Environment {
                        values,
                        used_keys: HashSet::new(),
                    },
                })))
            }
        }

        deserializer.deserialize_struct(
            "Environment",
            &["parent", "values"],
            ReadWriteEnvironmentVisitor(self.0),
        )
    }
}

impl<'de, 'a> DeserializeSeed<'de> for ReadWriteEnvironmentSequenceSeed<'a> {
    type Value = ();

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct EnvironmentSequenceVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);

        impl<'de, 'a> Visitor<'de> for EnvironmentSequenceVisitor<'a> {
            type Value = ();

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("sequence of struct Environment")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<(), V::Error>
            where
                V: SeqAccess<'de>,
            {
                {
                    let envs = self.0.last_mut().unwrap();
                    if let Some(size_hint) = seq.size_hint() {
                        envs.reserve(size_hint);
                    }
                }
                while let Some(elem) = seq.next_element_seed(ReadWriteEnvironmentSeed(self.0))? {
                    self.0.last_mut().unwrap().push(elem);
                }
                Ok(())
            }
        }

        deserializer.deserialize_seq(EnvironmentSequenceVisitor(self.0))
    }
}
