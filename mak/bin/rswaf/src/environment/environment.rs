use super::{Environment, EnvironmentValue, ReadWriteEnvironment};
use crate::node::Node;

use std::collections::{HashMap, HashSet};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use mlua::{Lua, IntoLua, Result, Value};

pub(super) enum EnvironmentParent {
    None,
    Current(Arc<Mutex<ReadWriteEnvironment>>),
    Parent(Arc<Mutex<ReadWriteEnvironment>>),
}

impl Environment {
    pub(crate) fn new() -> Self {
        Self {
            values: HashMap::new(),
            used_keys: HashSet::new(),
        }
    }

    pub(crate) fn get_into_list(
        self: &mut Self,
        key: &str,
    ) -> Vec<EnvironmentValue> {
        self.used_keys.insert(key.to_string());
        match self.values.get(key) {
            None => Vec::new(),
            Some(v) => v.clone().into_list(),
        }
    }

    pub(super) fn get_into_lua<'a, 'lua>(
        self: &'a mut Self,
        lua: &'lua Lua,
        key: &'a str,
    ) -> Result<Value<'lua>> {
        self.used_keys.insert(key.to_string());
        match self.values.get(key) {
            None => Ok(mlua::Nil),
            Some(v) => v.into_lua(lua),
        }
    }

    pub(crate) fn get_raw(self: &Self, key: &str) -> EnvironmentValue {
        match self.values.get(key) {
            None => EnvironmentValue::None,
            Some(v) => v.clone(),
        }
    }

    pub(crate) fn set(self: &mut Self, name: &str, value: EnvironmentValue) {
        self.values.insert(name.into(), value);
    }
}

impl ReadWriteEnvironment {
    pub(crate) fn new() -> Self {
        Self {
            parent: EnvironmentParent::None,
            index: 0,
            environment: Environment::new(),
        }
    }

    pub(crate) fn get_into_list(
        self: &mut Self,
        key: &str,
    ) -> Vec<EnvironmentValue> {
        self.environment.used_keys.insert(key.to_string());
        match self.environment.values.get(key) {
            None => match &self.parent {
                EnvironmentParent::None => Vec::new(),
                EnvironmentParent::Current(e) | EnvironmentParent::Parent(e) => {
                    e.lock().unwrap().get_into_list(key)
                }
            },
            Some(v) => v.clone().into_list(),
        }
    }

    pub(super) fn get_into_lua<'a, 'lua>(
        self: &'a mut Self,
        lua: &'lua Lua,
        key: &'a str,
    ) -> Result<Value<'lua>> {
        self.environment.used_keys.insert(key.to_string());
        match self.environment.values.get(key) {
            None => match &self.parent {
                EnvironmentParent::None => Ok(mlua::Nil),
                EnvironmentParent::Current(e) | EnvironmentParent::Parent(e) => {
                    e.lock().unwrap().get_into_lua(lua, key)
                }
            },
            Some(v) => v.into_lua(lua),
        }
    }

    pub(crate) fn get_raw(self: &Self, key: &str) -> EnvironmentValue {
        match self.environment.values.get(key) {
            None => match &self.parent {
                EnvironmentParent::None => EnvironmentValue::None,
                EnvironmentParent::Current(e) | EnvironmentParent::Parent(e) => {
                    e.lock().unwrap().get_raw(key)
                }
            },
            Some(v) => v.clone(),
        }
    }

    pub(crate) fn derive(from: &Arc<Mutex<ReadWriteEnvironment>>, index: usize) -> Self {
        Self {
            parent: EnvironmentParent::Current(from.clone()),
            index,
            environment: Environment::new(),
        }
    }

    pub(crate) fn derive_from_parent(from: &Arc<Mutex<ReadWriteEnvironment>>, index: usize) -> Self {
        Self {
            parent: EnvironmentParent::Parent(from.clone()),
            index,
            environment: Environment::new(),
        }
    }

    pub(crate) fn set(self: &mut Self, name: &str, value: EnvironmentValue) {
        self.environment.values.insert(name.into(), value);
    }
}

impl EnvironmentValue {
    pub(crate) fn from_lua(value: &Value) -> Result<Self> {
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
            EnvironmentValue::Node(n) => n.abs_path().to_string_lossy().to_string(),
            EnvironmentValue::Vec(v) => v
                .iter()
                .map(|v| v.as_string())
                .collect::<Vec<_>>()
                .join(" "),
        }
    }

    pub(crate) fn as_node(&self, current_dir: &Node) -> Result<Node> {
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
            EnvironmentValue::String(s) => Ok(current_dir.make_node(&PathBuf::from(s))),
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
            EnvironmentValue::Node(n) => vec![n.abs_path().to_string_lossy().to_string()],
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

    pub(crate) fn into_list(self) -> Vec<EnvironmentValue> {
        match self {
            EnvironmentValue::None => Vec::new(),
            EnvironmentValue::Vec(v) => v,
            _ => vec![self],
        }
    }
}
