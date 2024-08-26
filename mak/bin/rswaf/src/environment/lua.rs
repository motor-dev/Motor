use mlua::{IntoLua, Lua, MetaMethod, UserData, UserDataMethods, Value};
use crate::environment::{Environment, EnvironmentValue, ReadWriteEnvironment};

impl<'lua> IntoLua<'lua> for &EnvironmentValue {
    fn into_lua(self: Self, lua: &'lua Lua) -> mlua::Result<Value<'lua>> {
        match &self {
            EnvironmentValue::None => Ok(mlua::Nil),
            EnvironmentValue::Bool(value) => Ok(value.into_lua(lua)?),
            EnvironmentValue::Integer(value) => Ok(value.into_lua(lua)?),
            EnvironmentValue::String(value) => Ok(Value::String(lua.create_string(value)?)),
            EnvironmentValue::Node(value) => {
                Ok(Value::UserData(lua.create_userdata(value.clone())?))
            }
            EnvironmentValue::Vec(value) => Ok({
                let table = lua.create_table()?;
                for v in value {
                    table.push(v.into_lua(lua)?)?;
                }
                Value::Table(table)
            }),
        }
    }
}

impl UserData for Environment {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_method_mut(MetaMethod::Index, |lua, this, key: String| {
            this.get_into_lua(lua, key.as_str())
        });
    }
}

impl UserData for ReadWriteEnvironment {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_method_mut(
            "append",
            |_lua, this, (key, value): (String, Value)| {
                let mut original_value = this.get_into_list(key.as_str());
                let value = EnvironmentValue::from_lua(&value)?;
                original_value.push(value);
                Ok(this.set(key.as_str(), EnvironmentValue::Vec(original_value)))
            },
        );
        methods.add_meta_method_mut(MetaMethod::Index, |lua, this, key: String| {
            this.get_into_lua(lua, key.as_str())
        });
        methods.add_meta_method_mut(
            MetaMethod::NewIndex,
            |_lua, this, (key, value): (String, Value)| {
                Ok(this.set(key.as_str(), EnvironmentValue::from_lua(&value)?))
            },
        );
    }
}
