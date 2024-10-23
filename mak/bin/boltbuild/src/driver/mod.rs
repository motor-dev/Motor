use serde::{Deserialize, Serialize};
use crate::node::Node;

mod command;
mod lua;
mod msvc;
mod gcc;

#[derive(Serialize, Deserialize)]
enum DriverConfiguration {
    Command(command::CommandDriverConfiguration),
    GccCommand(gcc::GccCommandDriverConfiguration),
    MsvcCommand(msvc::MsvcCommandDriverConfiguration),
    Lua(lua::LuaDriverConfiguration),
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

    pub(crate) fn from_gcc_command(color: String, command: String) -> Self {
        Self {
            color,
            configuration: DriverConfiguration::GccCommand(gcc::GccCommandDriverConfiguration::new(command)),
        }
    }

    pub(crate) fn from_msvc_command(color: String, command: String) -> Self {
        Self {
            color,
            configuration: DriverConfiguration::MsvcCommand(msvc::MsvcCommandDriverConfiguration::new(command)),
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

    pub(crate) fn execute(&self) {
        match &self.configuration {
            DriverConfiguration::Command(cmd) => cmd.execute(),
            DriverConfiguration::GccCommand(cmd) => cmd.execute(),
            DriverConfiguration::MsvcCommand(cmd) => cmd.execute(),
            DriverConfiguration::Lua(cmd) => cmd.execute(),
        }
    }
}