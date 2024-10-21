use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct MsvcCommandDriverConfiguration {}

impl MsvcCommandDriverConfiguration {
    pub(super) fn execute(&self) {}
}
