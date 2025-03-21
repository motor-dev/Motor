use crate::node::Node;
use serde::Serialize;
use std::collections::{HashMap, HashSet};
use std::fmt::Display;
use std::sync::{Arc, Mutex, Weak};

mod derive;
mod get;
mod lua_binding;
pub(super) mod serialization;
mod value;

pub(crate) use get::Hash;
pub(crate) use get::Lookup;
pub(crate) use get::RawLookup;

#[derive(Clone)]
pub(crate) enum MapValue {
    None,
    Bool(bool),
    Integer(i64),
    String(String),
    Node(Node),
    Vec(Vec<MapValue>),
    Overlay(usize),
}

#[derive(Serialize, Clone)]
pub(crate) struct FlatMap {
    values: HashMap<String, MapValue>,
    #[serde(skip_serializing)]
    used_keys: HashSet<String>,
}

pub(crate) use serialization::OverlayMapVec;

pub(crate) struct OverlayMap {
    parent: OverlayParent,
    pub(crate) index: usize,
    environment: FlatMap,
    sub_envs: Vec<(usize, Weak<Mutex<OverlayMap>>)>,
}

impl FlatMap {
    pub(crate) fn new() -> Self {
        Self {
            values: HashMap::new(),
            used_keys: HashSet::new(),
        }
    }

    pub(crate) fn get_used_keys(&self) -> Vec<String> {
        self.used_keys.iter().cloned().collect()
    }
}

impl OverlayMap {
    pub(crate) fn new(index: usize) -> Self {
        Self {
            parent: OverlayParent::None,
            index,
            environment: FlatMap::new(),
            sub_envs: Vec::new(),
        }
    }

    pub(crate) fn get_used_keys(&self) -> Vec<String> {
        self.environment.used_keys.iter().cloned().collect()
    }
}

impl Display for OverlayMap {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", format!("env {}", self.index))
    }
}

pub(self) enum OverlayParent {
    None,
    Current(Arc<Mutex<OverlayMap>>),
    Parent(Arc<Mutex<OverlayMap>>),
    Leaf(Arc<Mutex<OverlayMap>>),
}
