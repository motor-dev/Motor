use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct GccCommandDriverConfiguration {
    command: String,
}

impl GccCommandDriverConfiguration {
    pub(super) fn new(command: String) -> Self {
        Self {
            command
        }
    }
    
    pub(super) fn execute(&self) {}
}
