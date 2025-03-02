use super::super::MapValue;
use super::overlay_map_seq::OverlayMapVec;
use super::value::MapValueSeed;
use serde::de::{DeserializeSeed, SeqAccess, Visitor};
use serde::Deserializer;
use std::fmt;

pub(super) struct MapValueVecSeed<'a>(pub(super) &'a mut OverlayMapVec);

impl<'de, 'a> DeserializeSeed<'de> for MapValueVecSeed<'a> {
    type Value = Vec<MapValue>;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct MapValueValueSequenceVisitor<'a>(&'a mut OverlayMapVec);

        impl<'de, 'a> Visitor<'de> for MapValueValueSequenceVisitor<'a> {
            type Value = Vec<MapValue>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("sequence of struct MapValue")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let mut result = Vec::new();
                if let Some(size_hint) = seq.size_hint() {
                    result.reserve(size_hint);
                }
                while let Some(elem) = seq.next_element_seed(MapValueSeed(self.0))? {
                    result.push(elem);
                }
                Ok(result)
            }
        }

        deserializer.deserialize_seq(MapValueValueSequenceVisitor(self.0))
    }
}
