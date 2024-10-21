use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct CommandDriverConfiguration {}

impl CommandDriverConfiguration {
    pub(super) fn execute(&self) {}
}
