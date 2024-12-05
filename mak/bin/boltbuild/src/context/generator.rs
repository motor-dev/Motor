use crate::command::GroupStatus;
use crate::context::operations::INVALID_CHARS;
use crate::context::Context;
use crate::environment::ReadWriteEnvironment;
use crate::generator::Generator;
use mlua::prelude::{LuaError, LuaResult, LuaTable, LuaValue};
use mlua::{AnyUserData, FromLua, Lua};
use std::ops::Deref;
use std::sync::{Arc, Mutex};

pub(super) fn declare_group(
    _lua: &Lua,
    this: &mut Context,
    (name, enabled): (String, LuaValue),
) -> LuaResult<()> {
    if INVALID_CHARS.find(&name).is_some() {
        Err(LuaError::RuntimeError(format!(
            "`{}`: invalid characters in group name",
            &name
        )))
    } else if this.output.groups.iter().any(|x| x.0.eq(&name)) {
        Err(LuaError::RuntimeError(format!(
            "`{}`: build group already registered",
            &name
        )))
    } else {
        let status = match enabled {
            LuaValue::Nil => GroupStatus::Default,
            LuaValue::Integer(i) => if i == 0 { GroupStatus::Disabled } else { GroupStatus::Enabled },
            LuaValue::Boolean(b) => if b { GroupStatus::Enabled } else { GroupStatus::Disabled },
            LuaValue::String(s) => GroupStatus::Conditional(s.to_string_lossy().to_string()),
            _ => return Err(LuaError::RuntimeError("Parameter `enabled` of method `declare_group` should be nil, a boolean, or a string".to_string())),
        };
        this.output.groups.push((name.to_string(), status));
        Ok(())
    }
}

pub(super) fn set_group_enabled(
    _lua: &Lua,
    this: &mut Context,
    (name, enabled): (String, LuaValue),
) -> LuaResult<()> {
    if let Some(group) = this.output.groups.iter_mut().find(|x| x.0.eq(&name)) {
        group.1 = match enabled {
            LuaValue::Nil => GroupStatus::Default,
            LuaValue::Integer(i) => if i == 0 { GroupStatus::Disabled } else { GroupStatus::Enabled },
            LuaValue::Boolean(b) => if b { GroupStatus::Enabled } else { GroupStatus::Disabled },
            LuaValue::String(s) => GroupStatus::Conditional(s.to_string_lossy().to_string()),
            _ => return Err(LuaError::RuntimeError("Parameter `enabled` of method `declare_group` should be nil, a boolean, or a string".to_string())),
        };
        Ok(())
    } else {
        Err(LuaError::RuntimeError(format!(
            "`{}`: build group already registered",
            &name
        )))
    }
}

pub(super) fn declare_generator(
    lua: &Lua,
    (this, name, features, env, group): (
        AnyUserData,
        String,
        LuaValue,
        Option<AnyUserData>,
        Option<String>,
    ),
) -> LuaResult<AnyUserData> {
    let group = this.borrow_mut_scoped::<Context, _>(|context| {
        let group = group.unwrap_or_else(|| context.spec.fs_name.clone());
        if !context.output.groups.iter().any(|x| x.0.eq(&group)) {
            return Err(LuaError::RuntimeError(format!(
                "When creating generator `{}`: `{}`: group was not declared",
                &name, group
            )));
        }
        Ok(group)
    })??;
    let features = match &features {
        LuaValue::String(s) => s
            .to_string_lossy()
            .split(',')
            .map(|x| x.trim().to_string())
            .collect(),
        LuaValue::Table(_) => Vec::<String>::from_lua(features, lua)?,
        LuaValue::Nil => Vec::new(),
        _ => {
            return Err(LuaError::RuntimeError(
                "features should be a list of string or a single string".to_string(),
            ))
        }
    };

    let generator = this.borrow_mut_scoped::<Context, _>(|this| {
        let from_env = if let Some(env) = env {
            env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?
                .deref()
                .clone()
        } else {
            this.environment.clone()
        };
        let env = Arc::new(Mutex::new(ReadWriteEnvironment::derive(
            &from_env,
            this.output.environments.len(),
        )?));
        this.output.environments.push(env.clone());
        lua.create_userdata(Arc::new(Mutex::new(Generator::new(
            name, this.path.clone(), env, group, features,
        ))))
    })??;

    generator.set_named_user_value(":context", &this)?;
    this.named_user_value::<LuaTable>(":generators")?
        .push(generator.clone())?;
    Ok(generator)
}

pub(super) fn get_generator_by_name(
    _lua: &Lua,
    (this, generator_name): (AnyUserData, String),
) -> LuaResult<Option<AnyUserData>> {
    let generators = this.named_user_value::<Vec<AnyUserData>>(":generators")?;
    for generator in generators {
        if generator
            .borrow::<Arc<Mutex<Generator>>>()?
            .lock()
            .unwrap()
            .name
            .eq(&generator_name)
        {
            return Ok(Some(generator));
        }
    }
    Ok(None)
}
