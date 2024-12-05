use crate::environment::ReadWriteEnvironment;
use crate::node::Node;
use std::sync::{Arc, Mutex};

mod lua_binding;

pub(crate) struct Generator {
    pub(crate) name: String,
    pub(crate) path: Node,
    pub(crate) group: String,
    pub(crate) env: Arc<Mutex<ReadWriteEnvironment>>,
    pub(crate) features: Vec<String>,
    pub(crate) posted: bool,
}

impl Generator {
    pub(crate) fn new(
        name: String,
        path: Node,
        env: Arc<Mutex<ReadWriteEnvironment>>,
        group: String,
        features: Vec<String>,
    ) -> Self {
        Self {
            name,
            path,
            group,
            env,
            features,
            posted: false,
        }
    }
}
