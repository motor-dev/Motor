use crate::context::Context;
use mlua::prelude::LuaResult;
use mlua::Lua;

#[cfg(feature = "lua_debug")]
extern "C" {
    pub fn emmy_tcp_listen(state: *mut mlua::lua_State) -> std::os::raw::c_int;
    pub fn emmy_tcp_connect(state: *mut mlua::lua_State) -> std::os::raw::c_int;
    pub fn emmy_wait_IDE(state: *mut mlua::lua_State) -> std::os::raw::c_int;
    pub fn emmy_break(state: *mut mlua::lua_State) -> std::os::raw::c_int;
}

#[cfg(feature = "lua_debug")]
pub(super) fn start_debug_server(
    lua: &Lua,
    this: &mut Context,
    (address, port): (Option<String>, Option<u16>),
) -> LuaResult<()> {
    unsafe {
        lua.exec_raw::<()>(
            (
                address.unwrap_or("127.0.0.1".to_string()),
                port.unwrap_or(9966),
            ),
            |state| {
                emmy_tcp_listen(state);
            },
        )?;
    }

    this.logger.set_status("waiting for IDE to connect");
    let result = unsafe {
        lua.exec_raw::<()>((), |state| {
            emmy_wait_IDE(state);
        })
    };
    this.logger.clear_status();
    if result.is_ok() {
        unsafe {
            lua.exec_raw::<()>((), |state| {
                emmy_break(state);
            })
        }
    } else {
        result
    }
}

#[cfg(feature = "lua_debug")]
pub(super) fn connect_to_debugger(
    lua: &Lua,
    this: &mut Context,
    (address, port): (Option<String>, Option<u16>),
) -> LuaResult<()> {
    this.logger.set_status("Connecting to debugger");
    let result = unsafe {
        lua.exec_raw::<()>(
            (
                address.unwrap_or("127.0.0.1".to_string()),
                port.unwrap_or(9966),
            ),
            |state| {
                emmy_tcp_connect(state);
            },
        )
    };
    this.logger.clear_status();
    result
}

#[cfg(not(feature = "lua_debug"))]
pub(super) fn start_debug_server(
    _lua: &Lua,
    _this: &mut Context,
    (_address, _port): (Option<String>, Option<u16>),
) -> LuaResult<()> {
    Err(mlua::Error::RuntimeError(
        "Lua debug is not enabled".to_string(),
    ))
}

#[cfg(not(feature = "lua_debug"))]
pub(super) fn connect_to_debugger(
    _lua: &Lua,
    _this: &mut Context,
    (_address, _port): (Option<String>, Option<u16>),
) -> LuaResult<()> {
    Err(mlua::Error::RuntimeError(
        "Lua debug is not enabled".to_string(),
    ))
}
