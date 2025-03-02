use super::super::OverlayMap;
use super::overlay_map::OverlayMapSeed;
use serde::de::{DeserializeSeed, SeqAccess, Visitor};
use serde::Deserializer;
use std::fmt;
use std::sync::{Arc, Mutex};

pub(crate) type OverlayMapVec = Vec<Arc<Mutex<OverlayMap>>>;

pub(crate) struct OverlayMapSequenceSeed<'a>(pub &'a OverlayMapVec);

impl<'de, 'a> DeserializeSeed<'de> for OverlayMapSequenceSeed<'a> {
    type Value = OverlayMapVec;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct OverlayMapSequenceVisitor<'a>(&'a OverlayMapVec);

        impl<'de, 'a> Visitor<'de> for OverlayMapSequenceVisitor<'a> {
            type Value = OverlayMapVec;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("sequence of struct OverlayMap")
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<Self::Value, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let mut result = OverlayMapVec::new();
                if let Some(size_hint) = seq.size_hint() {
                    result.reserve(size_hint);
                }
                while let Some(elem) = seq.next_element_seed(OverlayMapSeed {
                    current: &mut result,
                    parent: self.0,
                })? {
                    result.push(elem);
                }
                Ok(result)
            }
        }

        deserializer.deserialize_seq(OverlayMapSequenceVisitor(self.0))
    }
}
