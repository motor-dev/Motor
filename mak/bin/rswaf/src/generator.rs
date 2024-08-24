use mlua::{AnyUserData, MetaMethod, UserData, UserDataFields, UserDataMethods};
use mlua::prelude::{LuaError, LuaValue};

pub(crate) struct Generator {
    pub(crate) name: String,
    pub(crate) stage: String,
    pub(crate) features: Vec<String>,
    pub(crate) posted: bool,
}

impl Generator {
    pub(crate) fn new(name: String, stage: String, features: Vec<String>) -> Self {
        Self { name, stage, features, posted: false }
    }
}

impl UserData for Generator {
    fn add_fields<'lua, F: UserDataFields<'lua, Self>>(fields: &mut F) {
        fields.add_field_method_get("name", |_lua, this| Ok(this.name.clone()));
    }

    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_function_mut(MetaMethod::NewIndex, |_lua, (context, name, value): (AnyUserData, String, LuaValue)| {
            context.set_named_user_value(name.as_str(), value)
        });

        methods.add_meta_function_mut(MetaMethod::Index, |_lua, (context, name): (AnyUserData, String)| {
            let result = context.named_user_value::<LuaValue<'lua>>(name.as_str())?;
            if result.is_nil() {
                Err(LuaError::RuntimeError(format!("Context does not have a user value `{}`", name)))
            } else { Ok(result) }
        });
    }
}