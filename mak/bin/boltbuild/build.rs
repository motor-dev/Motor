#[cfg(feature = "lua_debug")]
extern crate cc;

fn main() {
    #[cfg(feature = "lua_debug")]
    {
        let mut debugger_build = cc::Build::new();
        debugger_build
            .cpp(true)
            .define("EMMY_USE_LUA_SOURCE", None)
            .define("EMMY_LUA_54", None)
            .file("emmy/emmy_debugger/src/api/lua_api.cpp")
            .file("emmy/emmy_debugger/src/api/lua_state.cpp")
            .file("emmy/emmy_debugger/src/api/lua_version.cpp")
            .file("emmy/emmy_debugger/src/api/lua_state/lua_state_54.cpp")
            .file("emmy/emmy_debugger/src/transporter/pipeline_client_transporter.cpp")
            .file("emmy/emmy_debugger/src/transporter/pipeline_server_transporter.cpp")
            .file("emmy/emmy_debugger/src/transporter/socket_client_transporter.cpp")
            .file("emmy/emmy_debugger/src/transporter/socket_server_transporter.cpp")
            .file("emmy/emmy_debugger/src/transporter/transporter.cpp")
            .file("emmy/emmy_debugger/src/debugger/emmy_debugger.cpp")
            .file("emmy/emmy_debugger/src/debugger/emmy_debugger_manager.cpp")
            .file("emmy/emmy_debugger/src/debugger/emmy_debugger_lib.cpp")
            .file("emmy/emmy_debugger/src/debugger/hook_state.cpp")
            .file("emmy/emmy_debugger/src/debugger/extension_point.cpp")
            .file("emmy/emmy_debugger/src/proto/proto.cpp")
            .file("emmy/emmy_debugger/src/proto/proto_handler.cpp")
            .file("emmy/emmy_debugger/src/arena/arena.cpp")
            .file("emmy/emmy_debugger/src/emmy_facade.cpp")
            .file("emmy/emmy_debugger/src/util.cpp")
            .include("emmy/emmy_debugger/include")
            .include("emmy/nlohmann/include")
            .include("emmy/libuv-1.46.0/include")
            .include("emmy/lua")
            .warnings(false);
        debugger_build.compile("emmy_debugger");

        cc::Build::new()
            .cpp(true)
            .file("emmy/emmy_core/src/emmy_core.cpp")
            .include("emmy/emmy_debugger/include")
            .include("emmy/nlohmann/include")
            .include("emmy/libuv-1.46.0/include")
            .warnings(false)
            .compile("emmy_core");

        println!("cargo::rerun-if-changed=emmy");
    }
}
