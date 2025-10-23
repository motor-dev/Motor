use crate::command::SerializedHash;
use crate::context::Context;
use crate::driver::Driver;
use crate::environment::OverlayMap;
use crate::node::Node;
use crate::task::{Task, ENV_RE, SPLIT_RE};
use mlua::prelude::{LuaError, LuaResult, LuaValue};
use mlua::{AnyUserData, FromLua, Lua};
use std::collections::hash_map::Entry;
use std::ops::Deref;
use std::sync::{Arc, Mutex};

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
        Err(LuaError::RuntimeError(format!(
            "invalid syntax in command {}",
            command
        )))
    }
}

pub(super) fn dependency_driver(
    _lua: &Lua,
    this: &mut Context,
    (name, color, command, dep_type, run_before): (
        String,
        String,
        String,
        String,
        Option<Vec<String>>,
    ),
) -> LuaResult<()> {
    if is_command_valid(command.as_str()) {
        insert_driver(
            this,
            name,
            Driver::from_dependency_command(color, command, dep_type),
            run_before,
        )
    } else {
        Err(LuaError::RuntimeError(format!(
            "invalid syntax in command {}",
            command
        )))
    }
}

pub(super) fn lua_driver(
    _lua: &Lua,
    this: &mut Context,
    (name, color, script, run_before): (String, String, Node, Option<Vec<String>>),
) -> LuaResult<()> {
    insert_driver(
        this,
        name,
        Driver::from_lua_script(color, script),
        run_before,
    )
}

fn insert_driver(
    context: &mut Context,
    name: String,
    driver: Driver,
    run_before: Option<Vec<String>>,
) -> LuaResult<()> {
    match context.output.drivers.entry(name) {
        Entry::Occupied(entry) => Err(LuaError::RuntimeError(format!(
            "Overriding tool {}",
            entry.key()
        ))),
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

pub(super) fn run_driver(
    lua: &Lua,
    context: &mut Context,
    (name, inputs, outputs, env): (String, LuaValue, LuaValue, Option<AnyUserData>),
) -> LuaResult<(u32, String)> {
    let driver = context
        .output
        .drivers
        .get(&name)
        .ok_or_else(|| LuaError::RuntimeError(format!("Tool {} not found", name)))?;
    let inputs = match &inputs {
        LuaValue::Nil => Vec::new(),
        LuaValue::Table(_) => Vec::<Node>::from_lua(inputs, lua)?,
        LuaValue::UserData(d) => vec![d.borrow::<Node>()?.clone()],
        _ => {
            return Err(LuaError::RuntimeError(
                "inputs should be a node or a list of nodes".to_string(),
            ))
        }
    };
    let outputs = match &outputs {
        LuaValue::Nil => Vec::new(),
        LuaValue::Table(_) => Vec::<Node>::from_lua(outputs, lua)?,
        LuaValue::UserData(d) => vec![d.borrow::<Node>()?.clone()],
        _ => {
            return Err(LuaError::RuntimeError(
                "outputs should be a node or a list of nodes".to_string(),
            ))
        }
    };
    let env = if let Some(env) = env {
        env.borrow::<Arc<Mutex<OverlayMap>>>()?.deref().clone()
    } else {
        context.environment.clone()
    };
    let mut env = OverlayMap::derive_leaf(&env)?;
    env.set("SRC", (&inputs).into());
    env.set("TGT", (&outputs).into());
    let task = Task {
        driver: name,
        generator: "context".to_string(),
        group: "context".to_string(),
        env: Arc::new(Mutex::new(env)),
        inputs,
        outputs,
        predecessors: Vec::new(),
        successors: Vec::new(),
        signature: SerializedHash(blake3::hash(&[])),
    };
    let result = driver.execute(&task);
    for input in &task.inputs {
        context
            .output
            .stored_hash
            .file_dependencies
            .push(input.path().clone());
    }
    for additional_input in &result.driver_dependencies {
        context
            .output
            .stored_hash
            .file_dependencies
            .push(additional_input.path().clone());
    }
    for additional_input in &result.file_dependencies {
        context
            .output
            .stored_hash
            .file_dependencies
            .push(additional_input.path().clone());
    }
    Ok((result.exit_code, result.log))
}
