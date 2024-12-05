use crate::driver::Output;
use crate::node::Node;
use crate::task::Task;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct UnzipDriverConfiguration {}

impl UnzipDriverConfiguration {
    pub(super) fn new() -> Self {
        Self {}
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        Output {
            exit_code: 1,
            command: String::new(),
            log: String::new(),
            driver_hash: self.hash(&[]),
            driver_dependencies: Vec::new(),
            file_dependencies: Vec::new(),
            extra_output: Vec::new(),
        }
    }

    pub(super) fn hash(&self, _: &[Node]) -> blake3::Hash {
        blake3::Hasher::new().finalize()
    }
}
