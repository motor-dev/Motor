use crate::node::Node;
use mlua::{IntoLua, Lua, MetaMethod, Result, UserData, UserDataMethods, Value};
use serde::de::{DeserializeSeed, MapAccess, SeqAccess, Visitor};
use serde::ser::SerializeStruct;
use serde::{de, Deserialize, Deserializer, Serialize, Serializer};
use std::collections::{HashMap, HashSet};
use std::fmt;
use std::path::PathBuf;
use std::result::Result as StdResult;
use std::sync::{Arc, Mutex};

enum EnvironmentParent {
    None,
    Current(Arc<Mutex<Environment>>),
    Parent(Arc<Mutex<Environment>>),
}

pub(crate) struct Environment {
    parent: EnvironmentParent,
    values: HashMap<String, EnvironmentValue>,
    pub(crate) used_keys: HashSet<String>,
    pub(crate) index: usize,
}

impl Environment {
    pub(crate) fn new() -> Self {
        Self {
            parent: EnvironmentParent::None,
            values: HashMap::new(),
            used_keys: HashSet::new(),
            index: 0,
        }
    }

    fn get_into_lua<'a, 'lua>(
        self: &'a mut Self,
        lua: &'lua Lua,
        key: &'a str,
    ) -> mlua::Result<Value<'lua>> {
        self.used_keys.insert(key.to_string());
        match self.values.get(key) {
            None => match &self.parent {
                EnvironmentParent::None => Ok(mlua::Nil),
                EnvironmentParent::Current(e) | EnvironmentParent::Parent(e) => {
                    e.lock().unwrap().get_into_lua(lua, key).clone()
                }
            },
            Some(v) => v.into_lua(lua),
        }
    }

    pub(crate) fn get_raw(self: &Self, key: &str) -> EnvironmentValue {
        match self.values.get(key) {
            None => match &self.parent {
                EnvironmentParent::None => EnvironmentValue::None,
                EnvironmentParent::Current(e) | EnvironmentParent::Parent(e) => {
                    e.lock().unwrap().get_raw(key)
                }
            },
            Some(v) => v.clone(),
        }
    }

    pub(crate) fn derive(from: &Arc<Mutex<Environment>>, index: usize) -> Self {
        Self {
            parent: EnvironmentParent::Current(from.clone()),
            values: HashMap::new(),
            used_keys: HashSet::new(),
            index,
        }
    }

    pub(crate) fn derive_from_parent(from: &Arc<Mutex<Environment>>, index: usize) -> Self {
        Self {
            parent: EnvironmentParent::Parent(from.clone()),
            values: HashMap::new(),
            used_keys: HashSet::new(),
            index,
        }
    }

    pub(crate) fn set(self: &mut Self, name: &str, value: EnvironmentValue) {
        self.values.insert(name.into(), value);
    }
}

#[derive(Serialize, Deserialize, Clone)]
pub(crate) enum EnvironmentValue {
    None,
    Bool(bool),
    Integer(i64),
    String(String),
    Node(Node),
    Vec(Vec<EnvironmentValue>),
}

impl EnvironmentValue {
    pub(crate) fn from_lua(value: &Value) -> mlua::Result<Self> {
        match value {
            Value::Nil => Ok(EnvironmentValue::None),
            Value::Boolean(b) => Ok(EnvironmentValue::Bool(*b)),
            Value::Integer(i) => Ok(EnvironmentValue::Integer(*i)),
            Value::String(s) => Ok(EnvironmentValue::String(s.to_str()?.to_string())),
            Value::Table(t) => {
                let mut result = Vec::<EnvironmentValue>::new();
                let mut index = 1;
                loop {
                    let v: Value = t.raw_get(index)?;
                    if v.is_nil() {
                        break;
                    }
                    result.push(Self::from_lua(&v)?);
                    index += 1;
                }
                if index < t.raw_len() {
                    Err(mlua::Error::RuntimeError(
                        "table contains key/value pairs".to_string(),
                    ))
                } else {
                    Ok(EnvironmentValue::Vec(result))
                }
            }
            Value::UserData(d) => Ok(EnvironmentValue::Node((*(d.borrow::<Node>()?)).clone())),
            _ => Err(mlua::Error::RuntimeError(format!(
                "invalid type for environment: {}",
                value.type_name(),
            ))),
        }
    }

    pub(crate) fn as_string(&self) -> String {
        match self {
            EnvironmentValue::None => "".to_string(),
            EnvironmentValue::Bool(b) => b.to_string(),
            EnvironmentValue::Integer(i) => i.to_string(),
            EnvironmentValue::String(s) => s.clone(),
            EnvironmentValue::Node(n) => n.abspath().to_string_lossy().to_string(),
            EnvironmentValue::Vec(v) => v
                .iter()
                .map(|v| v.as_string())
                .collect::<Vec<_>>()
                .join(" "),
        }
    }

    pub(crate) fn as_node(&self) -> Result<Node> {
        match self {
            EnvironmentValue::None => Err(mlua::Error::RuntimeError(
                "can't unpack value Nil as Node".to_string(),
            )),
            EnvironmentValue::Bool(_) => Err(mlua::Error::RuntimeError(
                "can't unpack Bool value as Node".to_string(),
            )),
            EnvironmentValue::Integer(_) => Err(mlua::Error::RuntimeError(
                "can't unpack Integer value as Node".to_string(),
            )),
            EnvironmentValue::String(s) => Ok(Node::from(&PathBuf::from(s))),
            EnvironmentValue::Node(n) => Ok(n.clone()),
            EnvironmentValue::Vec(_) => Err(mlua::Error::RuntimeError(
                "can't unpack Vector value as Node".to_string(),
            )),
        }
    }

    pub(crate) fn as_vec(&self) -> Vec<String> {
        match self {
            EnvironmentValue::None => Vec::new(),
            EnvironmentValue::Bool(b) => vec![b.to_string()],
            EnvironmentValue::Integer(i) => vec![i.to_string()],
            EnvironmentValue::String(s) => vec![s.clone()],
            EnvironmentValue::Node(n) => vec![n.abspath().to_string_lossy().to_string()],
            EnvironmentValue::Vec(v) => v.iter().map(|v| v.as_string()).collect::<Vec<_>>(),
        }
    }

    pub(crate) fn hash(&self, hasher: &mut blake3::Hasher) {
        match self {
            EnvironmentValue::None => hasher.update(b"nil"),
            EnvironmentValue::Bool(b) => {
                hasher
                    .update("bool".as_bytes())
                    .update(if *b { b"true" } else { b"false" })
            }
            EnvironmentValue::Integer(i) => hasher.update(b"int").update(&i.to_ne_bytes()),
            EnvironmentValue::String(s) => hasher.update(b"string").update(s.as_bytes()),
            EnvironmentValue::Node(n) => hasher
                .update(b"node")
                .update(n.path().as_os_str().as_encoded_bytes()),
            EnvironmentValue::Vec(v) => {
                hasher.update(b"vec").update(&v.len().to_ne_bytes());
                for value in v {
                    value.hash(hasher)
                }
                hasher
            }
        };
    }
}

impl<'lua> IntoLua<'lua> for &EnvironmentValue {
    fn into_lua(self: Self, lua: &'lua Lua) -> mlua::Result<Value<'lua>> {
        match &self {
            EnvironmentValue::None => Ok(mlua::Nil),
            EnvironmentValue::Bool(value) => Ok(value.into_lua(lua)?),
            EnvironmentValue::Integer(value) => Ok(value.into_lua(lua)?),
            EnvironmentValue::String(value) => Ok(Value::String(lua.create_string(value)?)),
            EnvironmentValue::Node(value) => {
                Ok(Value::UserData(lua.create_userdata(value.clone())?))
            }
            EnvironmentValue::Vec(value) => Ok({
                let table = lua.create_table()?;
                for v in value {
                    table.push(v.into_lua(lua)?)?;
                }
                Value::Table(table)
            }),
        }
    }
}

impl UserData for Environment {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_method_mut(MetaMethod::Index, |lua, this, key: String| {
            this.get_into_lua(lua, key.as_str())
        });
        methods.add_meta_method_mut(
            MetaMethod::NewIndex,
            |_lua, this, (key, value): (String, Value)| {
                Ok(this.set(key.as_str(), EnvironmentValue::from_lua(&value)?))
            },
        );
    }
}

pub(crate) struct SerializedEnvironment<'a>(pub(crate) &'a Arc<Mutex<Environment>>);

impl<'a> Serialize for SerializedEnvironment<'a> {
    fn serialize<S>(&self, serializer: S) -> StdResult<S::Ok, S::Error>
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
        s.serialize_field("values", &self.0.lock().unwrap().values)?;
        s.end()
    }
}

pub(crate) struct EnvironmentSeed<'a>(pub &'a Vec<Vec<Arc<Mutex<Environment>>>>);

#[derive(Serialize, Deserialize)]
enum SerializedEnvironmentParent {
    None,
    Current(usize),
    Parent(usize),
}

impl<'de, 'a> DeserializeSeed<'de> for EnvironmentSeed<'a> {
    type Value = Arc<Mutex<Environment>>;

    fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        enum Field {
            Parent,
            Values,
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
                        formatter.write_str("`parent`, or `values`")
                    }

                    fn visit_str<E>(self, value: &str) -> StdResult<Field, E>
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

        struct EnvironmentVisitor<'a>(&'a Vec<Vec<Arc<Mutex<Environment>>>>);

        impl<'de, 'a> Visitor<'de> for EnvironmentVisitor<'a> {
            type Value = Arc<Mutex<Environment>>;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct Environment")
            }

            fn visit_seq<V>(self, mut seq: V) -> StdResult<Arc<Mutex<Environment>>, V::Error>
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
                Ok(Arc::new(Mutex::new(Environment {
                    parent,
                    values,
                    used_keys: HashSet::new(),
                    index: 0,
                })))
            }

            fn visit_map<V>(self, mut map: V) -> StdResult<Arc<Mutex<Environment>>, V::Error>
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
                Ok(Arc::new(Mutex::new(Environment {
                    parent,
                    values,
                    used_keys: HashSet::new(),
                    index: 0,
                })))
            }
        }

        deserializer.deserialize_struct(
            "Environment",
            &["parent", "values"],
            EnvironmentVisitor(self.0),
        )
    }
}

pub(crate) struct EnvironmentSequenceSeed<'a>(pub &'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

impl<'de, 'a> DeserializeSeed<'de> for EnvironmentSequenceSeed<'a> {
    type Value = ();

    fn deserialize<D>(self, deserializer: D) -> StdResult<Self::Value, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct EnvironmentSequenceVisitor<'a>(&'a mut Vec<Vec<Arc<Mutex<Environment>>>>);

        impl<'de, 'a> Visitor<'de> for EnvironmentSequenceVisitor<'a> {
            type Value = ();

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("sequence of struct Environment")
            }

            fn visit_seq<V>(self, mut seq: V) -> StdResult<(), V::Error>
            where
                V: SeqAccess<'de>,
            {
                {
                    let envs = self.0.last_mut().unwrap();
                    if let Some(size_hint) = seq.size_hint() {
                        envs.reserve(size_hint);
                    }
                }
                while let Some(elem) = seq.next_element_seed(EnvironmentSeed(self.0))? {
                    self.0.last_mut().unwrap().push(elem);
                }
                Ok(())
            }
        }

        deserializer.deserialize_seq(EnvironmentSequenceVisitor(self.0))
    }
}
