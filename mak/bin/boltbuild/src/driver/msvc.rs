use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct MsvcCommandDriverConfiguration {
    command: String,
}

impl MsvcCommandDriverConfiguration {
    pub(super) fn new(command: String) -> Self {
        Self {
            command
        }
    }
    
    pub(super) fn execute(&self) {}
}
