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
    dependency_var: String,
}

impl DependencyCommandDriverConfiguration {
    pub(super) fn new(command: String, dependency_var: String) -> Self {
        Self {
            command,
            dependency_var,
        }
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let mut dep_node = task.outputs[0].clone();
        let dep_type = task
            .env
            .lock()
            .unwrap()
            .get(self.dependency_var.as_str())
            .as_string();
        let mut extra_options = Vec::new();
        match dep_type.as_str() {
            "msvc" => {
                dep_node.change_ext("json");
                extra_options.push("/sourceDependencies".to_string());
                extra_options.push(dep_node.to_string());
            }
            "gnu" => {
                dep_node.change_ext("d");
                extra_options.push("-MD".to_string());
                extra_options.push("-MF".to_string());
                extra_options.push(dep_node.to_string());
            }
            _ => {
                return Output {
                    exit_code: 1,
                    command: String::new(),
                    log: format!(
                        "unknown value `{}` for dependency variable `{}`",
                        dep_type, self.dependency_var
                    ),
                    driver_hash: self.hash(&[]),
                    driver_dependencies: Vec::new(),
                    file_dependencies: Vec::new(),
                    extra_output: Vec::new(),
                }
            }
        }
        let (exit_code, mut log, command) = task.run_command(self.command.as_str(), extra_options);
        if dep_type.eq("msvc") && exit_code == 0 {
            let mut line_count = 0;
            for c in log.chars() {
                if c == '\n' {
                    line_count += 1;
                    if line_count == 2 {
                        break;
                    }
                }
            }
            if line_count <= 1 {
                log.clear();
            }
        }
        if exit_code == 0 {
            Output {
                exit_code,
                command,
                log,
                driver_hash: self.hash(&[]),
                driver_dependencies: Vec::new(),
                file_dependencies: parse_dep(&dep_node, dep_type.as_str()),
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
            .update("version:1.0".as_bytes())
            .update(self.command.as_bytes())
            .finalize()
    }
}

fn parse_dep(dep_file: &Node, dep_type: &str) -> Vec<Node> {
    match dep_type {
        "msvc" => parse_msdep(dep_file),
        "gnu" => parse_makedep(dep_file),
        _ => unreachable!(),
    }
}

fn parse_msdep(dep_file: &Node) -> Vec<Node> {
    #[derive(Deserialize)]
    #[allow(unused)]
    struct DependencyInfo {
        #[serde(rename = "Source")]
        source: String,
        #[serde(rename = "ProvidedModule")]
        provided_module: String,
        #[serde(rename = "Includes")]
        includes: Vec<String>,
        #[serde(rename = "ImportedModules")]
        imported_modules: Option<Vec<String>>,
        #[serde(rename = "ImportedHeaderUnits")]
        imported_header_units: Option<Vec<String>>,
    }
    #[derive(Deserialize)]
    #[allow(unused)]
    struct Root {
        #[serde(rename = "Version")]
        version: String,
        #[serde(rename = "Data")]
        data: DependencyInfo,
    }
    let mut dependencies = Vec::new();
    let file = File::open(dep_file.abs_path()).unwrap();
    let root: Root = serde_json::from_reader(file).unwrap();
    if root.data.source.starts_with("\\\\wsl") {
        for dep in root.data.includes {
            if dep.starts_with("\\\\wsl") {
                let dep = dep.split('\\').skip(4).collect::<Vec<_>>().join("/");
                let dep_node = dep_file
                    .make_node(&PathBuf::from("/"))
                    .make_node(&PathBuf::from(dep))
                    .fix_case(); // due to Windows breaking the original case
                if !dep_node.is_file() {
                    println!("oops! {}", dep_node);
                } else {
                    dependencies.push(dep_node);
                }
            } else {
                let drive = dep.chars().next().unwrap().to_lowercase().to_string();
                let dep = dep.split('\\').skip(1).collect::<Vec<_>>().join("/");
                let dep_node = dep_file
                    .make_node(&PathBuf::from("/mnt"))
                    .make_node(&PathBuf::from(drive))
                    .make_node(&PathBuf::from(dep))
                    .fix_case(); // due to Windows breaking the original case
                if !dep_node.is_file() {
                    println!("oops! {}", dep_node);
                } else {
                    dependencies.push(dep_node);
                }
            }
        }
    }
    dependencies
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
