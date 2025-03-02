use super::super::MapValue;
use super::overlay_map_seq::OverlayMapVec;
use super::value_seq::MapValueVecSeed;
use serde::de::{DeserializeSeed, VariantAccess, Visitor};
use serde::{Deserializer, Serialize, Serializer};
use std::fmt;

impl Serialize for MapValue {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        match self {
            MapValue::None => serializer.serialize_unit_variant("MapValue", 0, "None"),
            MapValue::Bool(v) => serializer.serialize_newtype_variant("MapValue", 1, "Bool", v),
            MapValue::Integer(v) => {
                serializer.serialize_newtype_variant("MapValue", 2, "Integer", v)
            }
            MapValue::String(v) => serializer.serialize_newtype_variant("MapValue", 3, "String", v),
            MapValue::Node(v) => serializer.serialize_newtype_variant("MapValue", 4, "Node", v),
            MapValue::Vec(v) => serializer.serialize_newtype_variant("MapValue", 5, "Vec", v),
            MapValue::Overlay(v) => {
                serializer.serialize_newtype_variant("MapValue", 6, "Overlay", v)
            }
        }
    }
}

pub(super) struct MapValueSeed<'a>(pub(super) &'a mut OverlayMapVec);

impl<'de, 'a> DeserializeSeed<'de> for MapValueSeed<'a> {
    type Value = MapValue;

    fn deserialize<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct MapValueVisitor<'a>(&'a mut OverlayMapVec);

        impl<'de, 'a> Visitor<'de> for MapValueVisitor<'a> {
            type Value = MapValue;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("enum MapValue")
            }

            fn visit_enum<A>(self, data: A) -> Result<Self::Value, A::Error>
            where
                A: serde::de::EnumAccess<'de>,
            {
                let (variant, value) = data.variant::<u32>()?;
                match variant {
                    0 => {
                        value.unit_variant()?;
                        Ok(MapValue::None)
                    }
                    1 => Ok(MapValue::Bool(value.newtype_variant()?)),
                    2 => Ok(MapValue::Integer(value.newtype_variant()?)),
                    3 => Ok(MapValue::String(value.newtype_variant()?)),
                    4 => Ok(MapValue::Node(value.newtype_variant()?)),
                    5 => Ok(MapValue::Vec(
                        value.newtype_variant_seed(MapValueVecSeed(self.0))?,
                    )),
                    6 => {
                        let index = value.newtype_variant::<usize>()?;
                        if index < self.0.len() {
                            Ok(MapValue::Overlay(index))
                        } else {
                            Err(serde::de::Error::custom(format!(
                                "Overlay index out of bounds: {}",
                                index
                            )))
                        }
                    }
                    _ => Err(serde::de::Error::custom("invalid variant")),
                }
            }
        }

        deserializer.deserialize_enum(
            "MapValue",
            &[
                "None", "Bool", "Integer", "String", "Node", "Vec", "Overlay",
            ],
            MapValueVisitor(self.0),
        )
    }
}
