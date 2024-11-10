use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use crate::node::Node;
use crate::task::Task;

mod command;
mod lua;
mod dependency;

#[derive(Serialize, Deserialize)]
enum DriverConfiguration {
    Command(command::CommandDriverConfiguration),
    DependencyCommand(dependency::DependencyCommandDriverConfiguration),
    Lua(lua::LuaDriverConfiguration),
}

pub(crate) struct Output {
    pub(crate) exit_code: u32,
    pub(crate) command: String,
    pub(crate) log: String,
    pub(crate) file_dependencies: Vec<PathBuf>,
    pub(crate) extra_output: Vec<Node>,
}

#[derive(Serialize, Deserialize)]
pub(crate) struct Driver {
    color: String,
    configuration: DriverConfiguration,
}

impl Driver {
    pub(crate) fn from_command(color: String, command: String) -> Self {
        Self {
            color,
            configuration: DriverConfiguration::Command(command::CommandDriverConfiguration::new(command)),
        }
    }

    pub(crate) fn from_dependency_command(color: String, command: String) -> Self {
        Self {
            color,
            configuration: DriverConfiguration::DependencyCommand(dependency::DependencyCommandDriverConfiguration::new(command)),
        }
    }

    pub(crate) fn from_lua_script(color: String, script: Node) -> Self {
        Self {
            color,
            configuration: DriverConfiguration::Lua(lua::LuaDriverConfiguration::new(script)),
        }
    }

    pub(crate) fn get_color(&self) -> &str {
        self.color.as_str()
    }

    pub(crate) fn execute(&self, task: &Task) -> Output {
        match &self.configuration {
            DriverConfiguration::Command(cmd) => cmd.execute(task),
            DriverConfiguration::DependencyCommand(cmd) => cmd.execute(task),
            DriverConfiguration::Lua(cmd) => cmd.execute(task),
        }
    }
}