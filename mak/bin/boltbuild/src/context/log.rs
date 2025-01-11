use crate::context::Context;
use mlua::prelude::{LuaError, LuaFunction, LuaResult, LuaValue};
use mlua::{AnyUserData, Lua};

pub(super) fn debug(_lua: &Lua, this: &mut Context, message: String) -> LuaResult<()> {
    this.logger.debug(message.as_str());
    Ok(())
}

pub(super) fn info(_lua: &Lua, this: &mut Context, message: String) -> LuaResult<()> {
    this.logger.info(message.as_str());
    Ok(())
}

pub(super) fn warn(_lua: &Lua, this: &mut Context, message: String) -> LuaResult<()> {
    this.logger.warning(message.as_str());
    Ok(())
}

pub(super) fn error(_lua: &Lua, this: &mut Context, message: String) -> LuaResult<()> {
    this.logger.error(message.as_str());
    Ok(())
}

pub(super) fn raise_error(_lua: &Lua, _this: &mut Context, message: String) -> LuaResult<()> {
    Err(LuaError::RuntimeError(message))
}

pub(super) fn print(_lua: &Lua, this: &mut Context, message: String) -> LuaResult<()> {
    this.logger.print(message.as_str());
    Ok(())
}

pub(super) fn colored_println(_lua: &Lua, this: &mut Context, message: String) -> LuaResult<()> {
    this.logger.colored_println(message.as_str());
    Ok(())
}

pub(super) fn lua_try(_lua: &Lua, args: (AnyUserData, String, LuaFunction)) -> LuaResult<bool> {
    args.0.borrow_mut_scoped::<Context, _>(|this| {
        this.logger.begin(args.1.as_str());
    })?;
    let result: LuaResult<LuaValue> = args.2.call(());
    args.0
        .borrow_mut_scoped::<Context, _>(|this| match result {
            Ok(v) => {
                if v.is_nil() {
                    this.logger.end("Ok", true);
                } else {
                    this.logger.end(v.to_string()?.as_str(), true);
                }
                Ok(true)
            }
            Err(e) => {
                match &e {
                    LuaError::RuntimeError(s) => {
                        this.logger.end(s.as_str(), false);
                    }
                    LuaError::CallbackError {
                        traceback: _,
                        cause,
                    } => match cause.as_ref() {
                        LuaError::RuntimeError(s) => {
                            this.logger.end(s.as_str(), false);
                        }
                        _ => {
                            this.logger.end(e.to_string().as_str(), false);
                        }
                    },
                    _ => {
                        this.logger.end(e.to_string().as_str(), false);
                    }
                }
                Ok(false)
            }
        })?
}
