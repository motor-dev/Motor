use serde::{Deserialize, Serialize};
use crate::node::Node;

#[derive(Serialize, Deserialize)]
pub(super) struct LuaDriverConfiguration {
    script: Node
}

impl LuaDriverConfiguration {
    pub(super) fn new(script: Node) -> Self {
        Self {
            script
        }
    }

    pub(super) fn execute(&self) {}
}
