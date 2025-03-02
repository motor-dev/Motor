use super::super::MapValue;
use super::overlay_map_seq::OverlayMapVec;
use super::value::MapValueSeed;
use serde::de::{DeserializeSeed, MapAccess, Visitor};
use serde::Deserializer;
use std::collections::HashMap;
use std::fmt;

pub(super) struct MapValueMapSeed<'a>(pub(super) &'a mut OverlayMapVec);

impl<'de, 'a> DeserializeSeed<'de> for MapValueMapSeed<'a> {
    type Value = HashMap<String, MapValue>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct MapValueMapVisitor<'a>(&'a mut OverlayMapVec);

        impl<'de, 'a> Visitor<'de> for MapValueMapVisitor<'a> {
            type Value = HashMap<String, MapValue>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("map of struct MapValue")
            }

            fn visit_map<V>(self, mut map: V) -> Result<Self::Value, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut result = HashMap::new();
                while let Some(key) = map.next_key::<String>()? {
                    let value = map.next_value_seed(MapValueSeed(self.0))?;
                    result.insert(key, value);
                }
                Ok(result)
            }
        }

        deserializer.deserialize_map(MapValueMapVisitor(self.0))
    }
}
