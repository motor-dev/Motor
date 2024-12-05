use super::Output;
use crate::node::Node;
use crate::task::Task;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Read;
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
pub(super) struct DependencyCommandDriverConfiguration {
    command: String,
}

impl DependencyCommandDriverConfiguration {
    pub(super) fn new(command: String) -> Self {
        Self { command }
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let mut dep_node = task.outputs[0].clone();
        dep_node.change_ext("d");
        let (exit_code, log, command) =
            task.run_command(self.command.as_str(), vec![String::from("-MD")]);
        if exit_code == 0 {
            Output {
                exit_code,
                command,
                log,
                driver_hash: self.hash(&[]),
                driver_dependencies: Vec::new(),
                file_dependencies: parse_makedep(&dep_node),
                extra_output: vec![dep_node],
            }
        } else {
            Output {
                exit_code,
                command,
                log,
                driver_hash: self.hash(&[]),
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: vec![dep_node],
            }
        }
    }

    pub(super) fn hash(&self, _: &[Node]) -> blake3::Hash {
        blake3::Hasher::new()
            .update(self.command.as_bytes())
            .finalize()
    }
}

fn parse_makedep(dep_file: &Node) -> Vec<Node> {
    let mut dependencies = Vec::new();
    let mut file = File::open(dep_file.abs_path()).unwrap();
    let mut content = String::new();
    file.read_to_string(&mut content).unwrap();
    let mut content = content.chars();
    while let Some(c) = content.next() {
        if c.is_whitespace() {
            continue;
        }
        while let Some(c) = content.next() {
            if c.is_whitespace() {
                for c in content.by_ref() {
                    // find the ':'
                    if c.is_whitespace() {
                        continue;
                    } else if c == ':' {
                        break;
                    } else if c == '\\' {
                        continue;
                    } else {
                        unreachable!();
                    }
                }
            } else if c == ':' {
                if let Some(c) = content.next() {
                    if c.is_whitespace() {
                        break;
                    } else if c == '\\' {
                        if let Some(c) = content.next() {
                            if c.is_whitespace() {
                                break;
                            }
                        }
                    }
                }
            }
        }

        /* now looking for dependency file names */
        'eat_whitespace: while let Some(c) = content.next() {
            if c.is_whitespace() {
                continue 'eat_whitespace;
            } else if c == '\\' {
                if let Some(c) = content.next() {
                    if c == '\n' {
                        continue 'eat_whitespace;
                    }
                }
            } else if c == '"' {
                let mut file_name = String::new();
                while let Some(c) = content.next() {
                    if c == '"' {
                        dependencies.push(Node::from(&PathBuf::from(file_name)));
                        continue 'eat_whitespace;
                    } else if c == '\\' {
                        if let Some(c) = content.next() {
                            if c == '\n' {
                                dependencies.push(Node::from(&PathBuf::from(file_name)));
                                break;
                            } else {
                                file_name.push(c);
                            }
                        }
                    } else {
                        file_name.push(c);
                    }
                }
            }

            let mut file_name = String::new();
            file_name.push(c);
            while let Some(c) = content.next() {
                if c.is_whitespace() {
                    dependencies.push(Node::from(&PathBuf::from(file_name)));
                    break;
                } else if c == '\\' {
                    if let Some(c) = content.next() {
                        if c == '\n' {
                            dependencies.push(Node::from(&PathBuf::from(file_name)));
                            continue 'eat_whitespace;
                        } else {
                            file_name.push(c);
                        }
                    }
                } else {
                    file_name.push(c);
                }
            }
        }
    }
    dependencies
}
