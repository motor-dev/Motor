use super::super::{FlatMap, OverlayMap, OverlayParent};
use super::overlay_map_seq::OverlayMapVec;
use super::value_map::MapValueMapSeed;
use serde::de::{DeserializeSeed, Error, MapAccess, SeqAccess, Visitor};
use serde::ser::SerializeStruct;
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::collections::{BTreeMap, HashMap, HashSet};
use std::fmt;
use std::sync::{Arc, Mutex};

pub(crate) struct SerializedOverlayMap<'a>(pub(crate) &'a Arc<Mutex<OverlayMap>>);

impl<'a> Serialize for SerializedOverlayMap<'a> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut s = serializer.serialize_struct("OverlayMap", 2)?;
        s.serialize_field(
            "parent",
            &match &self.0.lock().unwrap().parent {
                OverlayParent::None => SerializedOverlayMapParent::None,
                OverlayParent::Current(p) => {
                    SerializedOverlayMapParent::Current(p.lock().unwrap().index)
                }
                OverlayParent::Parent(p) => {
                    SerializedOverlayMapParent::Parent(p.lock().unwrap().index)
                }
                OverlayParent::Leaf(p) => SerializedOverlayMapParent::Leaf(p.lock().unwrap().index),
            },
        )?;
        s.serialize_field(
            "values",
            &self
                .0
                .lock()
                .unwrap()
                .environment
                .values
                .iter()
                .collect::<BTreeMap<_, _>>(),
        )?;
        s.serialize_field(
            "sub_envs",
            &self
                .0
                .lock()
                .unwrap()
                .sub_envs
                .iter()
                .map(|env| env.0)
                .collect::<Vec<_>>(),
        )?;
        s.end()
    }
}

#[derive(Serialize, Deserialize)]
enum SerializedOverlayMapParent {
    None,
    Current(usize),
    Parent(usize),
    Leaf(usize),
}

pub(crate) struct OverlayMapSeed<'a> {
    pub current: &'a mut OverlayMapVec,
    pub parent: &'a OverlayMapVec,
    pub index: usize,
}

impl<'de, 'a> DeserializeSeed<'de> for OverlayMapSeed<'a> {
    type Value = Arc<Mutex<OverlayMap>>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Parent,
            Values,
            SubEnvs,
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
                        E: Error,
                    {
                        match value {
                            "parent" => Ok(Field::Parent),
                            "values" => Ok(Field::Values),
                            "sub_envs" => Ok(Field::SubEnvs),
                            _ => Err(Error::unknown_field(
                                value,
                                &["parent", "values", "sub_envs"],
                            )),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct OverlayMapVisitor<'a> {
            current: &'a mut OverlayMapVec,
            parent: &'a OverlayMapVec,
            index: usize,
        }

        impl<'de, 'a> Visitor<'de> for OverlayMapVisitor<'a> {
            type Value = Arc<Mutex<OverlayMap>>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct OverlayMap")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let parent = seq
                    .next_element::<SerializedOverlayMapParent>()?
                    .ok_or_else(|| Error::invalid_length(0, &self))?;
                let values = seq
                    .next_element_seed(MapValueMapSeed(self.current))?
                    .ok_or_else(|| Error::invalid_length(1, &self))?;
                let sub_envs = seq
                    .next_element::<Vec<usize>>()?
                    .ok_or_else(|| Error::invalid_length(2, &self))?;
                let sub_envs = sub_envs
                    .iter()
                    .map(|x| {
                        if *x >= self.current.len() {
                            self.current.resize_with(*x + 1, || {
                                Arc::new(Mutex::new(OverlayMap {
                                    parent: OverlayParent::None,
                                    index: usize::MAX,
                                    environment: FlatMap {
                                        values: HashMap::new(),
                                        used_keys: HashSet::new(),
                                    },
                                    sub_envs: Vec::new(),
                                }))
                            });
                        }
                        (*x, Arc::downgrade(&self.current[*x]))
                    })
                    .collect();
                let parent = match parent {
                    SerializedOverlayMapParent::None => OverlayParent::None,
                    SerializedOverlayMapParent::Current(index) => {
                        if self.current.len() <= index {
                            return Err(Error::custom(format!(
                                "invalid overlay index {}; expected an index in the range 0..{}",
                                index,
                                self.current.len()
                            )));
                        }
                        OverlayParent::Current(self.current[index].clone())
                    }
                    SerializedOverlayMapParent::Parent(index) => {
                        if self.parent.len() <= index {
                            return Err(Error::custom(format!(
                                "invalid overlay index {}; expected an index in the range 0..{}",
                                index,
                                self.parent.len()
                            )));
                        }
                        OverlayParent::Parent(self.parent[index].clone())
                    }
                    SerializedOverlayMapParent::Leaf(index) => {
                        if self.parent.len() <= index {
                            return Err(Error::custom(format!(
                                "invalid overlay index {}; expected an index in the range 0..{}",
                                index,
                                self.parent.len()
                            )));
                        }
                        OverlayParent::Leaf(self.parent[index].clone())
                    }
                };

                let result = OverlayMap {
                    parent,
                    index: self.index,
                    environment: FlatMap {
                        values,
                        used_keys: HashSet::new(),
                    },
                    sub_envs,
                };
                if self.index == self.current.len() {
                    let result = Arc::new(Mutex::new(result));
                    self.current.push(result.clone());
                    Ok(result)
                } else {
                    *self.current[self.index].lock().unwrap() = result;
                    Ok(self.current[self.index].clone())
                }
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut parent = None;
                let mut values = None;
                let mut sub_envs = None;
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Parent => {
                            if parent.is_some() {
                                return Err(Error::duplicate_field("parent"));
                            }
                            parent = Some(map.next_value()?);
                        }
                        Field::Values => {
                            if values.is_some() {
                                return Err(Error::duplicate_field("values"));
                            }
                            values = Some(map.next_value_seed(MapValueMapSeed(self.current))?);
                        }
                        Field::SubEnvs => {
                            if sub_envs.is_some() {
                                return Err(Error::duplicate_field("sub_envs"));
                            }
                            sub_envs = Some(
                                map.next_value::<Vec<usize>>()?
                                    .iter()
                                    .map(|x| {
                                        if *x >= self.current.len() {
                                            self.current.resize_with(*x + 1, || {
                                                Arc::new(Mutex::new(OverlayMap {
                                                    parent: OverlayParent::None,
                                                    index: usize::MAX,
                                                    environment: FlatMap {
                                                        values: HashMap::new(),
                                                        used_keys: HashSet::new(),
                                                    },
                                                    sub_envs: Vec::new(),
                                                }))
                                            });
                                        }
                                        (*x, Arc::downgrade(&self.current[*x]))
                                    })
                                    .collect(),
                            );
                        }
                    }
                }
                let parent = parent.ok_or_else(|| Error::missing_field("parent"))?;
                let parent = match parent {
                    SerializedOverlayMapParent::None => OverlayParent::None,
                    SerializedOverlayMapParent::Current(index) => {
                        if self.current.len() <= index {
                            return Err(Error::custom(format!("invalid environment index {}; expected an index in the range 0..{}", index, self.current.len())));
                        }
                        OverlayParent::Current(self.current[index].clone())
                    }
                    SerializedOverlayMapParent::Parent(index) => {
                        if self.parent.len() <= index {
                            return Err(Error::custom(format!("invalid environment index {}; expected an index in the range 0..{}", index, self.parent.len())));
                        }
                        OverlayParent::Parent(self.parent[index].clone())
                    }
                    SerializedOverlayMapParent::Leaf(index) => {
                        if self.parent.len() <= index {
                            return Err(Error::custom(format!("invalid environment index {}; expected an index in the range 0..{}", index, self.parent.len())));
                        }
                        OverlayParent::Leaf(self.parent[index].clone())
                    }
                };
                let values = values.ok_or_else(|| Error::missing_field("values"))?;
                let sub_envs = sub_envs.ok_or_else(|| Error::missing_field("sub_envs"))?;

                let result = OverlayMap {
                    parent,
                    index: self.index,
                    environment: FlatMap {
                        values,
                        used_keys: HashSet::new(),
                    },
                    sub_envs,
                };
                if self.index == self.current.len() {
                    let result = Arc::new(Mutex::new(result));
                    self.current.push(result.clone());
                    Ok(result)
                } else {
                    *self.current[self.index].lock().unwrap() = result;
                    Ok(self.current[self.index].clone())
                }
            }
        }

        deserializer.deserialize_struct(
            "Environment",
            &["parent", "values", "sub_envs"],
            OverlayMapVisitor {
                current: self.current,
                parent: self.parent,
                index: self.index,
            },
        )
    }
}
