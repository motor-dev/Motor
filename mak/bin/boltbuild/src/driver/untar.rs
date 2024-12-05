use crate::driver::Output;
use crate::node::Node;
use crate::task::Task;
use flate2::read::GzDecoder;
use serde::{Deserialize, Serialize};
use std::ops::Deref;
use std::path::PathBuf;
use tar::Archive;

#[derive(Serialize, Deserialize)]
pub(super) struct UntarDriverConfiguration {}

impl UntarDriverConfiguration {
    pub(super) fn new() -> Self {
        Self {}
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let driver_hash = self.hash(&[]);

        if task.inputs.len() != 1 {
            return Output {
                exit_code: 1,
                command: "tar xf".to_string(),
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
                command: format!("tar xf {}", input_file),
                log: "Expected exactly one input file".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }
        let output_dir = &task.outputs[0];

        match unpack(input_file, output_dir) {
            Ok(output) => Output {
                exit_code: 0,
                command: format!("tar xf {} => {}", input_file, output_dir),
                log: "".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: output,
            },
            Err(x) => Output {
                exit_code: 1,
                command: format!("tar xf {} => {}", input_file, output_dir),
                log: x,
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            },
        }
    }

    pub(super) fn hash(&self, _: &[Node]) -> blake3::Hash {
        blake3::Hasher::new().finalize()
    }
}

fn unpack(input_file: &Node, output_dir: &Node) -> Result<Vec<Node>, String> {
    let mut outputs = Vec::new();
    let dst = &output_dir
        .path()
        .canonicalize()
        .unwrap_or(output_dir.path().clone());
    std::fs::File::open(input_file.abs_path())
        .map_err(|e| e.to_string())
        .and_then(|file| {
            let archive = GzDecoder::new(file);
            let mut archive = Archive::new(archive);
            let mut directories = Vec::new();
            for entry in archive.entries().map_err(|e| e.to_string())? {
                let mut entry = entry.map_err(|e| e.to_string())?;
                if entry.header().entry_type().is_dir() {
                    directories.push(entry);
                } else if entry.unpack_in(dst).map_err(|e| e.to_string())? {
                    outputs.push(output_dir.make_node(&PathBuf::from(
                        entry.path().map_err(|e| e.to_string())?.deref(),
                    )));
                }
            }
            directories.sort_by(|a, b| b.path_bytes().cmp(&a.path_bytes()));
            for mut dir in directories {
                dir.unpack_in(dst).map_err(|x| x.to_string())?;
            }
            Ok(outputs)
        })
}
