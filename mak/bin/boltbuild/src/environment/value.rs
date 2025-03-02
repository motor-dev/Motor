use crate::environment::{MapValue, OverlayMap};
use crate::node::Node;
use mlua::{IntoLua, Lua, Value};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

impl MapValue {
    pub(crate) fn from_lua(value: &Value) -> mlua::Result<Self> {
        match value {
            Value::Nil => Ok(MapValue::None),
            Value::Boolean(b) => Ok(MapValue::Bool(*b)),
            Value::Integer(i) => Ok(MapValue::Integer(*i)),
            Value::String(s) => Ok(MapValue::String(s.to_str()?.to_string())),
            Value::Table(t) => {
                let mut result = Vec::<MapValue>::new();
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
                    Ok(MapValue::Vec(result))
                }
            }
            Value::UserData(d) => Ok(MapValue::Node((*(d.borrow::<Node>()?)).clone())),
            _ => Err(mlua::Error::RuntimeError(format!(
                "invalid type for environment: {}",
                value.type_name(),
            ))),
        }
    }

    pub(super) fn as_bool(&self) -> Option<bool> {
        match self {
            MapValue::None => None,
            MapValue::Bool(b) => Some(*b),
            MapValue::Integer(i) => Some(*i != 0),
            MapValue::String(s) => Some(!s.is_empty()),
            MapValue::Node(_) => Some(true),
            MapValue::Vec(v) => Some(!v.is_empty()),
            MapValue::Overlay(_) => Some(true),
        }
    }

    pub(super) fn as_string(&self, sub_envs: &[Arc<Mutex<OverlayMap>>]) -> String {
        match self {
            MapValue::None => "".to_string(),
            MapValue::Bool(b) => b.to_string(),
            MapValue::Integer(i) => i.to_string(),
            MapValue::String(s) => s.clone(),
            MapValue::Node(n) => n.nice_path().to_string_lossy().to_string(),
            MapValue::Vec(v) => v
                .iter()
                .map(|v| v.as_string(sub_envs))
                .collect::<Vec<_>>()
                .join(" "),
            MapValue::Overlay(v) => sub_envs[*v].lock().unwrap().to_string(),
        }
    }

    pub(super) fn as_node(&self, current_dir: &Node) -> Option<Node> {
        match self {
            MapValue::None => None,
            MapValue::Bool(_) => None,
            MapValue::Integer(_) => None,
            MapValue::String(s) => Some(current_dir.make_node(&PathBuf::from(s))),
            MapValue::Node(n) => Some(n.clone()),
            MapValue::Vec(_) => None,
            MapValue::Overlay(_) => None,
        }
    }

    pub(super) fn as_string_vec(&self, sub_envs: &[Arc<Mutex<OverlayMap>>]) -> Vec<String> {
        match self {
            MapValue::None => Vec::new(),
            MapValue::Bool(b) => vec![b.to_string()],
            MapValue::Integer(i) => vec![i.to_string()],
            MapValue::String(s) => vec![s.clone()],
            MapValue::Node(n) => vec![n.abs_path().to_string_lossy().to_string()],
            MapValue::Vec(v) => v.iter().map(|v| v.as_string(sub_envs)).collect::<Vec<_>>(),
            MapValue::Overlay(_) => Vec::new(),
        }
    }

    pub(super) fn as_node_vec(&self, current_dir: &Node) -> Vec<Node> {
        match self {
            MapValue::None => Vec::new(),
            MapValue::Bool(_) => Vec::new(),
            MapValue::Integer(_) => Vec::new(),
            MapValue::String(s) => vec![current_dir.make_node(&PathBuf::from(s))],
            MapValue::Node(n) => vec![n.clone()],
            MapValue::Vec(v) => v
                .iter()
                .map(|v| v.as_node(current_dir))
                .flatten()
                .collect::<Vec<_>>(),
            MapValue::Overlay(_) => Vec::new(),
        }
    }

    pub(super) fn as_int(&self) -> i64 {
        match self {
            MapValue::None => 0,
            MapValue::Bool(b) => *b as i64,
            MapValue::Integer(i) => *i,
            MapValue::String(s) => s.parse().unwrap_or(0),
            MapValue::Node(_) => 0,
            MapValue::Vec(_) => 0,
            MapValue::Overlay(_) => 0,
        }
    }

    pub(super) fn hash(&self, sub_envs: &Vec<Arc<Mutex<OverlayMap>>>, hasher: &mut blake3::Hasher) {
        match self {
            MapValue::None => hasher.update(b"nil"),
            MapValue::Bool(b) => {
                hasher
                    .update("bool".as_bytes())
                    .update(if *b { b"true" } else { b"false" })
            }
            MapValue::Integer(i) => hasher.update(b"int").update(&i.to_ne_bytes()),
            MapValue::String(s) => hasher.update(b"string").update(s.as_bytes()),
            MapValue::Node(n) => hasher
                .update(b"node")
                .update(n.path().as_os_str().as_encoded_bytes()),
            MapValue::Vec(v) => {
                hasher.update(b"vec").update(&v.len().to_ne_bytes());
                for value in v {
                    value.hash(sub_envs, hasher)
                }
                hasher
            }
            MapValue::Overlay(env) => hasher
                .update(b"env")
                .update(&sub_envs[*env].lock().unwrap().index.to_ne_bytes()),
        };
    }

    pub(super) fn into_list(self) -> Vec<MapValue> {
        match self {
            MapValue::None => Vec::new(),
            MapValue::Vec(v) => v,
            _ => vec![self],
        }
    }

    pub(super) fn get_into_lua(
        &self,
        sub_envs: &[Arc<Mutex<OverlayMap>>],
        lua: &Lua,
    ) -> mlua::Result<Value> {
        match self {
            MapValue::None => Ok(mlua::Nil),
            MapValue::Bool(value) => Ok(value.into_lua(lua)?),
            MapValue::Integer(value) => Ok(value.into_lua(lua)?),
            MapValue::String(value) => Ok(Value::String(lua.create_string(value)?)),
            MapValue::Node(value) => Ok(Value::UserData(lua.create_userdata(value.clone())?)),
            MapValue::Vec(value) => Ok({
                let table = lua.create_table()?;
                for v in value {
                    table.push(v.get_into_lua(sub_envs, lua)?)?;
                }
                Value::Table(table)
            }),
            MapValue::Overlay(value) => Ok(Value::UserData(
                lua.create_userdata(sub_envs[*value].clone())?,
            )),
        }
    }

    pub(super) fn is_none(&self) -> bool {
        matches!(&self, MapValue::None)
    }
    pub(super) fn is_list(&self) -> bool {
        matches!(&self, MapValue::Vec(_))
    }
}
