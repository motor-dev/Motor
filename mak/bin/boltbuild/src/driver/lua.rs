use super::Output;
use crate::node::Node;
use crate::task::Task;

use std::path::{Path, PathBuf};
use mlua::{Lua, Table};
use mlua::prelude::LuaValue;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct LuaDriverConfiguration {
    script: Node,
}

impl LuaDriverConfiguration {
    pub(super) fn new(script: Node) -> Self {
        Self {
            script
        }
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let lua = Lua::new();
        let globals = lua.globals();

        if let Err(err) = lua.scope(|scope| {
            let userdata = scope.create_userdata_ref(task).unwrap();
            let chunk = lua.load(self.script.path().as_path());
            chunk.call::<_, ()>(userdata)
        }) {
            Output {
                exit_code: 1,
                command: self.script.to_string(),
                log: err.to_string(),
                dependencies: Vec::new(),
            }
        } else {
            /* retrieve a list of modules */
            let mut dependencies = Vec::new();

            let package: Table = globals.get("package").unwrap();
            let package_path: String = package.get("path").unwrap();
            let packages: Table = package.get("loaded").unwrap();
            if let Err(err) = packages.for_each(|key: String, _: LuaValue| {
                for path in package_path.split(';') {
                    let module_path = path.replace("?", key.replace(".", "/").as_str());

                    if Path::new(module_path.as_str()).is_file() {
                        dependencies.push(PathBuf::from(module_path));
                        break;
                    }
                }
                Ok(())
            }) {
                Output {
                    exit_code: 1,
                    command: self.script.to_string(),
                    log: err.to_string(),
                    dependencies: Vec::new(),
                }
            } else {
                Output {
                    exit_code: 0,
                    command: self.script.to_string(),
                    log: "".to_string(),
                    dependencies,
                }
            }
        }
    }
}
