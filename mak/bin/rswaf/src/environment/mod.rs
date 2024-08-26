mod lua;
mod serialization;
mod environment;

use self::environment::EnvironmentParent;
use crate::node::Node;

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};


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

pub(crate) struct SerializedReadWriteEnvironment<'a>(pub(crate) &'a Arc<Mutex<ReadWriteEnvironment>>);
pub(crate) struct ReadWriteEnvironmentSequenceSeed<'a>(pub &'a mut Vec<Vec<Arc<Mutex<ReadWriteEnvironment>>>>);
