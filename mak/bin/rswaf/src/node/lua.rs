use super::Node;

use std::path::{Path, PathBuf};
use mlua::{Error, FromLua, Lua, MetaMethod, UserData, UserDataMethods, UserDataRef, Value};
use mlua::prelude::LuaError;

impl UserData for Node {
    fn add_fields<'lua, F: mlua::UserDataFields<'lua, Self>>(fields: &mut F) {
        fields.add_field_method_get("parent", |_lua, this| {
            let mut result = this.clone();
            result.path.pop();
            Ok(result)
        })
    }

    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_method(MetaMethod::ToString, |_lua, this: &Node, ()| {
            Ok(this.abs_path().to_string_lossy().to_string())
        });
        methods.add_method("make_node", |_lua, this, lua_path: String| {
            let path = Path::new(lua_path.as_str());
            let mut result = this.clone();
            result.path.push(path);
            Ok(result)
        });
        methods.add_method("abs_path", |_lua, this, ()| {
            Ok(this.path.to_string_lossy().to_string())
        });
        methods.add_method("path_from", |_, this: &Node, base: UserDataRef<Node>| {
            use std::path::Component;
            assert!(this.path.is_absolute());
            assert!(base.path.is_absolute());

            let mut ita = this.path.components();
            let mut itb = base.path.components();
            let mut comps: Vec<Component> = vec![];
            loop {
                match (ita.next(), itb.next()) {
                    (None, None) => break,
                    (Some(a), None) => {
                        comps.push(a);
                        comps.extend(ita.by_ref());
                        break;
                    }
                    (None, _) => comps.push(Component::ParentDir),
                    (Some(a), Some(b)) if comps.is_empty() && a == b => (),
                    (Some(a), Some(b)) if b == Component::CurDir => comps.push(a),
                    (Some(_), Some(b)) if b == Component::ParentDir => {
                        return Err(Error::RuntimeError(String::from(
                            "can't get relative path from {} to {}",
                        )))
                    }
                    (Some(a), Some(_)) => {
                        comps.push(Component::ParentDir);
                        for _ in itb {
                            comps.push(Component::ParentDir);
                        }
                        comps.push(a);
                        comps.extend(ita.by_ref());
                        break;
                    }
                }
            }

            Ok(String::from(
                PathBuf::from_iter(comps.iter().map(|c| c.as_os_str())).to_string_lossy(),
            ))
        });
        methods.add_method("name", |_lua, this: &Node, ()| Ok(this.path.file_name().and_then(|x| Some(x.to_string_lossy().to_string()))));
        methods.add_method("is_dir", |_lua, this: &Node, ()| Ok(this.is_dir()));
        methods.add_method("is_file", |_lua, this: &Node, ()| Ok(this.is_file()));
        methods.add_method("delete", |_lua, this: &Node, ()|
            this.delete().map_err(|x| LuaError::RuntimeError(x.to_string())),
        );
        methods.add_method("try_delete", |_lua, this: &Node, ()|
            this.delete().or(Ok(())),
        );
        methods.add_method("mkdir", |_lua, this: &Node, ()|
            this.mkdir().map_err(|x| LuaError::RuntimeError(x.to_string())),
        );
    }
}

impl<'lua> FromLua<'lua> for Node {
    fn from_lua(value: Value<'lua>, _lua: &'lua Lua) -> mlua::Result<Self> {
        match value {
            Value::UserData(userdata) => userdata.take::<Node>(),
            _ => Err(Error::FromLuaConversionError {
                from: value.type_name(),
                to: "Node",
                message: None,
            }),
        }
    }
}
