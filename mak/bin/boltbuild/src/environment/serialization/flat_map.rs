use super::super::FlatMap;
use super::overlay_map_seq::OverlayMapVec;
use super::value_map::MapValueMapSeed;
use serde::de::{DeserializeSeed, Error, MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer};
use std::collections::HashSet;
use std::fmt;

pub(crate) struct FlatMapSeed<'a>(pub(crate) &'a mut OverlayMapVec);

impl<'de, 'a> DeserializeSeed<'de> for FlatMapSeed<'a> {
    type Value = Option<FlatMap>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
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
                        formatter.write_str("`values`")
                    }

                    fn visit_str<E>(self, value: &str) -> Result<Field, E>
                    where
                        E: Error,
                    {
                        match value {
                            "values" => Ok(Field::Values),
                            _ => Err(Error::unknown_field(value, &["values"])),
                        }
                    }
                }

                deserializer.deserialize_identifier(FieldVisitor)
            }
        }

        struct FlatMapVisitor<'a>(&'a mut OverlayMapVec);

        impl<'de, 'a> Visitor<'de> for FlatMapVisitor<'a> {
            type Value = Option<FlatMap>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct FlatMap")
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
                deserializer.deserialize_struct("FlatMap", &["values"], self)
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let values = seq
                    .next_element_seed(MapValueMapSeed(self.0))?
                    .ok_or_else(|| Error::invalid_length(1, &self))?;
                Ok(Some(FlatMap {
                    values,
                    used_keys: HashSet::new(),
                }))
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut values = None;
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Values => {
                            if values.is_some() {
                                return Err(Error::duplicate_field("values"));
                            }
                            values = Some(map.next_value_seed(MapValueMapSeed(self.0))?);
                        }
                    }
                }
                let values = values.ok_or_else(|| Error::missing_field("values"))?;
                Ok(Some(FlatMap {
                    values,
                    used_keys: HashSet::new(),
                }))
            }
        }

        deserializer.deserialize_option(FlatMapVisitor(self.0))
    }
}
