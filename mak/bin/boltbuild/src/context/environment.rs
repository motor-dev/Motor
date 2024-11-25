use crate::context::Context;
use crate::environment::ReadWriteEnvironment;
use mlua::prelude::{LuaError, LuaFunction, LuaResult, LuaValue};
use mlua::{AnyUserData, Lua};
use std::ops::Deref;
use std::sync::{Arc, Mutex};

pub(super) fn derive(
    _lua: &Lua,
    this: &mut Context,
    env: Option<AnyUserData>,
) -> LuaResult<Arc<Mutex<ReadWriteEnvironment>>> {
    let from_env = if let Some(env) = env {
        env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?
            .deref()
            .clone()
    } else {
        this.environment.clone()
    };
    let new_env = Arc::new(Mutex::new(ReadWriteEnvironment::derive(
        &from_env,
        this.output.environments.len(),
    )?));
    this.output.environments.push(new_env.clone());
    Ok(new_env)
}

pub(super) fn with(
    _lua: &Lua,
    (context, env, function): (AnyUserData, AnyUserData, LuaFunction),
) -> LuaResult<LuaValue> {
    let prev_env = context.borrow_mut_scoped::<Context, _>(|context| {
        let env = env.borrow_mut::<Arc<Mutex<ReadWriteEnvironment>>>()?;
        let prev_env = context.environment.clone();
        context.environment = env.clone();
        drop(env);
        Ok::<_, LuaError>(prev_env)
    })??;
    let result: LuaResult<LuaValue> = function.call(());
    context.borrow_mut_scoped::<Context, _>(|context| {
        context.environment = prev_env;
    })?;
    result
}
