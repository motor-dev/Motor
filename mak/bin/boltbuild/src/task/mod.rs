mod lua_binding;
mod serialization;

use std::fmt::{Display, Formatter};
use std::sync::{Arc, Mutex};
use crate::command::SerializedHash;
use crate::environment::{ReadWriteEnvironment, ReadWriteEnvironmentVec};
use crate::node::Node;

pub(crate) struct Task {
    pub(crate) driver: String,
    pub(crate) generator: String,
    pub(crate) group: String,
    pub(crate) env: Arc<Mutex<ReadWriteEnvironment>>,
    pub(crate) inputs: Vec<Node>,
    pub(crate) outputs: Vec<Node>,
    pub(crate) predecessors: Vec<usize>,
    pub(crate) successors: Vec<usize>,
    pub(crate) signature: SerializedHash,
}

pub(crate) struct TaskHandle(pub(crate) usize);

pub(crate) struct TaskSeed<'a>(pub &'a ReadWriteEnvironmentVec);

impl Display for Task {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}/{}] {} ", self.group, self.generator, self.driver)?;
        for (index, path) in self.inputs.iter().enumerate() {
            if index != 0 { write!(f, ", ")?; }
            write!(f, "{}", path)?;
        }
        write!(f, " -> ")?;
        for (index, path) in self.outputs.iter().enumerate() {
            if index != 0 { write!(f, ", ")?; }
            write!(f, "{}", path)?;
        }
        Ok(())
    }
}
