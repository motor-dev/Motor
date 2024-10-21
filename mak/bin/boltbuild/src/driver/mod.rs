use serde::{Deserialize, Serialize};

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
    configuration: DriverConfiguration,
}

impl Driver {
    pub(crate) fn execute(&self) {
        match &self.configuration {
            DriverConfiguration::Command(cmd) => cmd.execute(),
            DriverConfiguration::GccCommand(cmd) => cmd.execute(),
            DriverConfiguration::MsvcCommand(cmd) => cmd.execute(),
            DriverConfiguration::Lua(cmd) => cmd.execute(),
        }
    }
}