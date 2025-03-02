use super::CommandLineParser;
use crate::environment::MapValue;
use mlua::{AnyUserData, MetaMethod, Result, UserData, UserDataMethods};
use std::sync::{Arc, Mutex};

struct InterfaceIndex(usize);

impl UserData for InterfaceIndex {
    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_function("set_long", |_lua, (this, long): (AnyUserData, String)| {
            let parser = this.user_value::<AnyUserData>()?;
            let parser = parser.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
            let mut parser = parser.lock().unwrap();
            let argument = &mut parser.options[this.borrow::<InterfaceIndex>()?.0];
            let interface = argument.interface.as_mut().unwrap();
            interface.set_long(long);
            Ok(this)
        });
        methods.add_function("set_short", |_lua, (this, short): (AnyUserData, String)| {
            let parser = this.user_value::<AnyUserData>()?;
            let parser = parser.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
            let mut parser = parser.lock().unwrap();
            let argument = &mut parser.options[this.borrow::<InterfaceIndex>()?.0];
            let interface = argument.interface.as_mut().unwrap();
            interface.set_short(short);
            Ok(this)
        });
        methods.add_function(
            "set_category",
            |_lua, (this, category): (AnyUserData, String)| {
                let parser = this.user_value::<AnyUserData>()?;
                let parser = parser.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
                let mut parser = parser.lock().unwrap();
                let argument = &mut parser.options[this.borrow::<InterfaceIndex>()?.0];
                let interface = argument.interface.as_mut().unwrap();
                interface.set_category(category);
                Ok(this)
            },
        );
        methods.add_function("set_required", |_lua, this: AnyUserData| {
            let parser = this.user_value::<AnyUserData>()?;
            let parser = parser.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
            let mut parser = parser.lock().unwrap();
            let argument = &mut parser.options[this.borrow::<InterfaceIndex>()?.0];
            let interface = argument.interface.as_mut().unwrap();
            interface.set_required();
            Ok(this)
        });
    }
}

impl UserData for CommandLineParser {
    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_meta_method_mut(
            MetaMethod::NewIndex,
            |_lua, this, (key, value): (String, mlua::Value)| -> Result<()> {
                if this.options.iter().position(|x| x.name.eq(&key)).is_some() {
                    this.map.set(&key, MapValue::from_lua(&value)?);
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
                if this.options.iter().position(|x| x.name.eq(&key)).is_some() {
                    this.map.get_into_lua(lua, &key)
                } else {
                    Err(mlua::Error::RuntimeError(
                        format!("'{}': no option registered with this name", key).to_string(),
                    ))
                }
            },
        );

        methods.add_function(
            "add_flag",
            |lua, args: (AnyUserData, String, String, Option<bool>)| {
                let result = {
                    let this = args.0.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
                    let mut this = this.lock().unwrap();
                    let default = if let Some(value) = args.3 {
                        MapValue::Bool(value)
                    } else {
                        MapValue::None
                    };
                    this.add_flag(args.1, args.2, default)?;
                    lua.create_userdata(InterfaceIndex(this.options.len() - 1))?
                };
                result.set_user_value(args.0)?;
                Ok(result)
            },
        );

        methods.add_function(
            "add_value",
            |_lua, args: (AnyUserData, String, String, mlua::Value)| {
                let result = {
                    let this = args.0.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
                    let mut this = this.lock().unwrap();
                    this.add_value(args.1, args.2, MapValue::from_lua(&args.3)?)?;
                    _lua.create_userdata(InterfaceIndex(this.options.len() - 1))?
                };
                result.set_user_value(args.0)?;
                Ok(result)
            },
        );

        methods.add_function(
            "add_count",
            |lua, args: (AnyUserData, String, String, mlua::Value)| {
                let result = {
                    let this = args.0.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
                    let mut this = this.lock().unwrap();
                    this.add_count(args.1, args.2, MapValue::from_lua(&args.3)?)?;
                    lua.create_userdata(InterfaceIndex(this.options.len() - 1))?
                };
                result.set_user_value(args.0)?;
                Ok(result)
            },
        );

        methods.add_function(
            "add_list",
            |lua, args: (AnyUserData, String, String, mlua::Value)| {
                let result = {
                    let this = args.0.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
                    let mut this = this.lock().unwrap();
                    this.add_list(args.1, args.2, MapValue::from_lua(&args.3)?)?;
                    lua.create_userdata(InterfaceIndex(this.options.len() - 1))?
                };
                result.set_user_value(args.0)?;
                Ok(result)
            },
        );

        methods.add_function(
            "add_choice",
            |lua, args: (AnyUserData, String, String, Vec<String>, mlua::Value)| {
                let result = {
                    let this = args.0.borrow_mut::<Arc<Mutex<CommandLineParser>>>()?;
                    let mut this = this.lock().unwrap();
                    this.add_choice(
                        args.1,
                        args.2,
                        args.3.as_slice(),
                        MapValue::from_lua(&args.4)?,
                    )?;
                    lua.create_userdata(InterfaceIndex(this.options.len() - 1))?
                };
                result.set_user_value(args.0)?;
                Ok(result)
            },
        );
    }
}
