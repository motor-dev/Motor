use crate::driver::Output;
use crate::node::Node;
use crate::task::Task;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct CopyDriverConfiguration {}

impl CopyDriverConfiguration {
    pub(super) fn new() -> Self {
        Self {}
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let driver_hash = self.hash(&[]);

        if task.inputs.len() != 1 {
            return Output {
                exit_code: 1,
                command: "copy".to_string(),
                log: "Expected exactly one input file".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }

        let input_file = &task.inputs[0];
        if task.outputs.len() != 1 {
            return Output {
                exit_code: 1,
                command: format!("copy {}", input_file),
                log: "Expected exactly one output file".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }
        let output_node = &task.outputs[0];
        let command = format!("copy {} -> {}", input_file, output_node);

        if let Err(e) = std::fs::copy(input_file.abs_path(), output_node.abs_path()) {
            Output {
                exit_code: 1,
                command,
                log: e.to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            }
        } else {
            Output {
                exit_code: 0,
                command,
                log: "".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            }
        }
    }

    pub(super) fn hash(&self, _: &[Node]) -> blake3::Hash {
        blake3::Hasher::new()
            .update("version:1.0".as_bytes())
            .finalize()
    }
}
