use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct LuaDriverConfiguration {}

impl LuaDriverConfiguration {
    pub(super) fn execute(&self) {}
}
