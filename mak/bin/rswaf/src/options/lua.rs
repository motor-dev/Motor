use super::CommandLineParser;
use crate::environment::EnvironmentValue;
use mlua::{IntoLua, Result, MetaMethod, UserData, UserDataMethods};

impl UserData for CommandLineParser {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_method_mut(
            MetaMethod::NewIndex,
            |_lua, this, (key, value): (String, mlua::Value)| -> Result<()> {
                if let Some(index) = this.options.iter().position(|x| x.name.eq(&key)) {
                    this.options[index].default = EnvironmentValue::from_lua(&value)?;
                    Ok(())
                } else {
                    Err(mlua::Error::RuntimeError(
                        format!("'{}': no option registered with this name", key).to_string(),
                    ))
                }
            },
        );
        methods.add_meta_method_mut(
            MetaMethod::Index,
            |lua, this, key: String| -> Result<mlua::Value> {
                if let Some(index) = this.options.iter().position(|x| x.name.eq(&key)) {
                    this.options[index].default.into_lua(lua)
                } else {
                    Err(mlua::Error::RuntimeError(
                        format!("'{}': no option registered with this name", key).to_string(),
                    ))
                }
            },
        );
        methods.add_method_mut(
            "add_flag",
            |_lua, this, args: (String, String, Option<String>, Option<String>, Option<String>, Option<bool>)|
             -> Result<()> {
                let default = if let Some(value) = args.5 {
                    EnvironmentValue::Bool(value)
                } else {
                    EnvironmentValue::None
                };
                this.add_flag(args.0, args.1, args.2, args.3, args.4, false, default)
            },
        );
        methods.add_method_mut(
            "add_value",
            |_lua, this, args: (String, String, Option<String>, Option<String>, Option<String>, mlua::Value)|
             -> Result<()> {
                this.add_value(args.0, args.1, args.2, args.3, args.4, false, EnvironmentValue::from_lua(&args.5)?)
            },
        );
        methods.add_method_mut(
            "add_count",
            |_lua,
             this,
             args: (String, String, Option<String>, Option<String>, Option<String>, mlua::Value)|
             -> Result<()> {
                this.add_count(args.0, args.1, args.2, args.3, args.4, false, EnvironmentValue::from_lua(&args.5)?)
            },
        );
        methods.add_method_mut(
            "add_list",
            |_lua, this, args: (String, String, Option<String>, Option<String>, Option<String>, mlua::Value)|
             -> Result<()> {
                this.add_list(args.0, args.1, args.2, args.3, args.4, false, EnvironmentValue::from_lua(&args.5)?)
            },
        );
        methods.add_method_mut(
            "add_choice",
            |_lua, this, args: (String, String, Vec<String>, Option<String>, Option<String>, Option<String>, mlua::Value)|
             -> Result<()> {
                this.add_choice(args.0, args.1, args.3, args.4, args.5, false, args.2, EnvironmentValue::from_lua(&args.6)?,
                )
            },
        );
    }
}
