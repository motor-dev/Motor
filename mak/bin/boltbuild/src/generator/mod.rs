use crate::environment::ReadWriteEnvironment;
use std::sync::{Arc, Mutex};

mod lua_binding;

pub(crate) struct Generator {
    pub(crate) name: String,
    pub(crate) group: String,
    pub(crate) env: Arc<Mutex<ReadWriteEnvironment>>,
    pub(crate) features: Vec<String>,
    pub(crate) posted: bool,
}

impl Generator {
    pub(crate) fn new(
        name: String,
        env: Arc<Mutex<ReadWriteEnvironment>>,
        group: String,
        features: Vec<String>,
    ) -> Self {
        Self {
            name,
            group,
            env,
            features,
            posted: false,
        }
    }
}
