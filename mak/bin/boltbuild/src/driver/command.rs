use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct CommandDriverConfiguration {
    command: String,
}

impl CommandDriverConfiguration {
    pub(super) fn new(command: String) -> Self {
        Self {
            command
        }
    }
    
    pub(super) fn execute(&self) {}
}
