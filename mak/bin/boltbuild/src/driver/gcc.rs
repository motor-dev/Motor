use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct GccCommandDriverConfiguration {}

impl GccCommandDriverConfiguration {
    pub(super) fn execute(&self) {}
}
