use super::command::*;
use super::driver::*;
use super::environment::*;
use super::feature::*;
use super::generator::*;
use super::log::*;
use super::node::*;
use super::subprocess::*;
use super::debug::*;
use super::Context;
use crate::options::Options;
use mlua::{AnyUserData, IntoLua, UserData, UserDataFields, UserDataMethods};

impl UserData for Context {
    fn add_fields<F: UserDataFields<Self>>(fields: &mut F) {
        fields.add_field_method_get("name", |_, this| Ok(this.spec.name.clone()));
        fields.add_field_method_get("fs_name", |_, this| Ok(this.spec.fs_name.clone()));
        fields.add_field_method_get("fun", |_, this| Ok(this.spec.function.clone()));
        fields.add_field_method_get("env", |_, this| Ok(this.environment.clone()));
        fields.add_field_method_get("path", |_, this| Ok(this.path.clone()));
        fields.add_field_method_get("src_dir", |_, this| Ok(this.src_dir.clone()));
        fields.add_field_method_get("bld_dir", |_, this| Ok(this.bld_dir.clone()));
        fields.add_field_method_get("settings", |lua, this| match &this.options {
            Options::CommandLineParser(context) => context.clone().into_lua(lua),
            Options::Environment(env) => env.clone().into_lua(lua),
        });
    }

    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_function("recurse", recurse);
        methods.add_method_mut("declare_command", declare_command);
        methods.add_method_mut("chain_command", chain_command);
        methods.add_method_mut("derive", derive);
        methods.add_method_mut("debug", debug);
        methods.add_method_mut("info", info);
        methods.add_method_mut("warn", warn);
        methods.add_method_mut("error", error);
        methods.add_method_mut("raise_error", raise_error);
        methods.add_method_mut("print", print);
        methods.add_method_mut("colored_print", colored_print);
        methods.add_function_mut("with", with);
        methods.add_function("try", lua_try);
        methods.add_method_mut("search", search);
        methods.add_method_mut("find_program", find_program);
        methods.add_method_mut("popen", popen);
        methods.add_function("load_tool", load_tool);
        methods.add_function("declare_generator", declare_generator);
        methods.add_function("feature", feature);
        methods.add_function("get_generator_by_name", get_generator_by_name);
        methods.add_function(
            "post",
            |lua, (this, generator): (AnyUserData, AnyUserData)| post(lua, (&this, &generator)),
        );
        methods.add_method_mut("declare_group", declare_group);
        methods.add_method_mut("set_group_enabled", set_group_enabled);
        methods.add_method_mut("command_driver", command_driver);
        methods.add_method_mut("dependency_driver", dependency_driver);
        methods.add_method_mut("lua_driver", lua_driver);
        methods.add_method("run_driver", run_driver);
        methods.add_method_mut("start_debug_server", start_debug_server);
        methods.add_method_mut("connect_to_debugger", connect_to_debugger);
    }
}
