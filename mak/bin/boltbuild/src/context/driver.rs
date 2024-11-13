use mlua::Lua;
use mlua::prelude::{LuaError, LuaResult};
use crate::context::Context;
use crate::driver::Driver;
use crate::node::Node;

use crate::task::{SPLIT_RE, ENV_RE};

fn is_command_valid(command: &str) -> bool {
    for argument in SPLIT_RE.split(command) {
        let mut iter = ENV_RE.find_iter(argument);
        if iter.next().is_some() && iter.next().is_some() {
            return false;
        }
    }
    true
}

pub(super) fn command_driver(_lua: &Lua, this: &mut Context, (name, color, command): (String, String, String)) -> LuaResult<()> {
    if is_command_valid(command.as_str()) {
        if this.output.drivers.insert(name.clone(), Driver::from_command(color, command)).is_some() {
            this.logger.info(format!("Overriding tool {}", name).as_str());
        }
        Ok(())
    } else {
        Err(LuaError::RuntimeError(format!("invalid syntax in command {}", command).to_string()))
    }
}

pub(super) fn dependency_driver(_lua: &Lua, this: &mut Context, (name, color, command): (String, String, String)) -> LuaResult<()> {
    if is_command_valid(command.as_str()) {
        if this.output.drivers.insert(name.clone(), Driver::from_dependency_command(color, command)).is_some() {
            this.logger.info(format!("Overriding tool {}", name).as_str());
        }
        Ok(())
    } else {
        Err(LuaError::RuntimeError(format!("invalid syntax in command {}", command).to_string()))
    }
}

pub(super) fn lua_driver(_lua: &Lua, this: &mut Context, (name, color, script): (String, String, Node)) -> LuaResult<()> {
    if this.output.drivers.insert(name.clone(), Driver::from_lua_script(color, script)).is_some() {
        this.logger.info(format!("Overriding tool {}", name).as_str());
    }
    Ok(())
}