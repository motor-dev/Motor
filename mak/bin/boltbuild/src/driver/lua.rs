use super::Output;
use crate::node::Node;
use crate::task::Task;
use mlua::prelude::LuaValue;
use mlua::{Lua, Table};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

#[derive(Serialize, Deserialize)]
pub(super) struct LuaDriverConfiguration {
    script: Node,
}

impl LuaDriverConfiguration {
    pub(super) fn new(script: Node) -> Self {
        Self { script }
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let lua = Lua::new();
        let globals = lua.globals();

        match lua.scope(|scope| {
            let userdata = scope.create_userdata_ref(task).unwrap();
            let chunk = lua.load(self.script.path().as_path());
            chunk.call::<(u32, Option<Vec<Node>>)>(userdata)
        }) {
            Err(err) => Output {
                exit_code: 1,
                command: self.script.to_string(),
                log: err.to_string(),
                hash: self.hash(&[]),
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            },
            Ok((result, file_dependencies)) => {
                /* retrieve a list of modules */
                let file_dependencies = file_dependencies.unwrap_or_else(Vec::new);

                let mut lua_dependencies = Vec::new();
                lua_dependencies.push(Node::from(self.script.path()));

                let package: Table = globals.get("package").unwrap();
                let package_path: String = package.get("path").unwrap();
                let packages: Table = package.get("loaded").unwrap();
                if let Err(err) = packages.for_each(|key: String, _: LuaValue| {
                    for path in package_path.split(';') {
                        let module_path = path.replace("?", key.replace(".", "/").as_str());

                        if Path::new(module_path.as_str()).is_file() {
                            lua_dependencies.push(Node::from(&PathBuf::from(module_path)));
                            break;
                        }
                    }
                    Ok(())
                }) {
                    Output {
                        exit_code: 1,
                        command: self.script.to_string(),
                        log: err.to_string(),
                        hash: self.hash(&[]),
                        driver_dependencies: Vec::new(),
                        file_dependencies: Vec::new(),
                        extra_output: Vec::new(),
                    }
                } else {
                    Output {
                        exit_code: result,
                        command: self.script.to_string(),
                        log: "".to_string(),
                        hash: self.hash(lua_dependencies.as_slice()),
                        driver_dependencies: lua_dependencies,
                        file_dependencies,
                        extra_output: Vec::new(),
                    }
                }
            }
        }
    }

    pub(super) fn hash(&self, dependencies: &[Node]) -> blake3::Hash {
        let mut hasher = blake3::Hasher::new();
        for dependency in dependencies {
            hasher.update(dependency.path().as_os_str().as_encoded_bytes());
            let file = std::fs::File::open(dependency.path()).unwrap();
            hasher.update_reader(file).unwrap();
        }
        hasher.finalize()
    }
}
