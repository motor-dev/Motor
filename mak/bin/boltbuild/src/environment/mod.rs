use self::lua_interop::EnvironmentParent;
use crate::node::Node;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};

mod lua_binding;
mod lua_interop;
mod serialization;

#[derive(Serialize, Deserialize, Clone)]
pub(crate) struct Environment {
    values: HashMap<String, EnvironmentValue>,
    #[serde(skip_serializing, skip_deserializing)]
    pub(crate) used_keys: HashSet<String>,
}

pub(crate) struct ReadWriteEnvironment {
    parent: EnvironmentParent,
    pub(crate) index: usize,
    pub(crate) environment: Environment,
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

pub(crate) type ReadWriteEnvironmentVec = Vec<Arc<Mutex<ReadWriteEnvironment>>>;

pub(crate) struct SerializedReadWriteEnvironment<'a>(
    pub(crate) &'a Arc<Mutex<ReadWriteEnvironment>>,
);
pub(crate) struct ReadWriteEnvironmentSeed<'a> {
    pub current: &'a ReadWriteEnvironmentVec,
    pub parent: &'a ReadWriteEnvironmentVec,
}
pub(crate) struct ReadWriteEnvironmentSequenceSeed<'a>(pub &'a ReadWriteEnvironmentVec);

impl Environment {
    pub(crate) fn new() -> Self {
        Self {
            values: HashMap::new(),
            used_keys: HashSet::new(),
        }
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
}
