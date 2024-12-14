use crate::driver::Output;
use crate::node::Node;
use crate::task::Task;
use rc_zip_sync::rc_zip::parse::Mode;
use rc_zip_sync::ReadZip;
use serde::{Deserialize, Serialize};
use std::io::Write;
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
pub(super) struct UnzipDriverConfiguration {}

impl UnzipDriverConfiguration {
    pub(super) fn new() -> Self {
        Self {}
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let driver_hash = self.hash(&[]);

        if task.inputs.len() != 1 {
            return Output {
                exit_code: 1,
                command: "unzip".to_string(),
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
                command: format!("unzip {}", input_file),
                log: "Expected exactly one output directory".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }
        let output_dir = &task.outputs[0];
        let command = format!("unzip {} => {}", input_file, output_dir);
        if let Err(e) = output_dir.mkdir() {
            return Output {
                exit_code: 1,
                command,
                log: e.to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }

        match unpack(input_file, output_dir) {
            Ok(output) => Output {
                exit_code: 0,
                command,
                log: "".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: output,
            },
            Err(x) => Output {
                exit_code: 1,
                command,
                log: x,
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            },
        }
    }

    pub(super) fn hash(&self, _: &[Node]) -> blake3::Hash {
        blake3::Hasher::new()
            .update("version:1.0".as_bytes())
            .finalize()
    }
}

fn unpack(input_file: &Node, output_dir: &Node) -> Result<Vec<Node>, String> {
    let mut outputs = Vec::new();
    std::fs::File::open(input_file.abs_path())
        .map_err(|e| e.to_string())
        .and_then(|file| {
            let archive = file.read_zip().map_err(|e| e.to_string())?;
            for entry in archive.entries() {
                if let Some(name) = entry.sanitized_name() {
                    let output = output_dir.make_node(&PathBuf::from(name));
                    if entry.mode & Mode::DIR == Mode::DIR {
                        output.mkdir().unwrap();
                    } else {
                        let mut file =
                            std::fs::File::create(output.abs_path()).map_err(|e| e.to_string())?;
                        let bytes = entry.bytes().map_err(|e| e.to_string())?;
                        file.write_all(&bytes).map_err(|e| e.to_string())?;
                        outputs.push(output);
                    }
                } else {
                    return Err("Invalid file name in archive".to_string());
                }
            }

            Ok(outputs)
        })
}
