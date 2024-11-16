use std::collections::hash_map::Entry;
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

pub(super) fn command_driver(
    _lua: &Lua,
    this: &mut Context,
    (name, color, command, run_before): (String, String, String, Option<Vec<String>>),
) -> LuaResult<()> {
    if is_command_valid(command.as_str()) {
        insert_driver(this, name, Driver::from_command(color, command), run_before)
    } else {
        Err(LuaError::RuntimeError(format!("invalid syntax in command {}", command)))
    }
}

pub(super) fn dependency_driver(
    _lua: &Lua,
    this: &mut Context,
    (name, color, command, run_before): (String, String, String, Option<Vec<String>>),
) -> LuaResult<()> {
    if is_command_valid(command.as_str()) {
        insert_driver(this, name, Driver::from_dependency_command(color, command), run_before)
    } else {
        Err(LuaError::RuntimeError(format!("invalid syntax in command {}", command)))
    }
}

pub(super) fn lua_driver(
    _lua: &Lua,
    this: &mut Context,
    (name, color, script, run_before): (String, String, Node, Option<Vec<String>>),
) -> LuaResult<()> {
    insert_driver(this, name, Driver::from_lua_script(color, script), run_before)
}

fn insert_driver(
    context: &mut Context,
    name: String,
    driver: Driver,
    run_before: Option<Vec<String>>,
) -> LuaResult<()> {
    match context.output.drivers.entry(name) {
        Entry::Occupied(entry) => {
            Err(LuaError::RuntimeError(format!("Overriding tool {}", entry.key())))
        }
        Entry::Vacant(entry) => {
            if let Some(run_before_list) = run_before {
                for dependency in run_before_list {
                    context.driver_order.push((entry.key().clone(), dependency));
                }
            }
            entry.insert(driver);
            Ok(())
        }
    }
}