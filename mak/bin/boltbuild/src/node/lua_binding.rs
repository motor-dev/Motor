use super::Node;
use mlua::prelude::{LuaError, LuaString};
use mlua::{Error, FromLua, Lua, MetaMethod, UserData, UserDataMethods, UserDataRef, Value};
use std::io::{Read, Write};
use std::ops::Deref;
use std::path::PathBuf;

impl UserData for Node {
    fn add_fields<F: mlua::UserDataFields<Self>>(fields: &mut F) {
        fields.add_field_method_get("parent", |_lua, this| {
            let mut result = this.clone();
            result.path.pop();
            Ok(result)
        });
    }

    fn add_methods<'lua, M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_meta_method(MetaMethod::ToString, |_lua, this: &Node, ()| {
            Ok(this.nice_path().to_string_lossy().to_string())
        });
        methods.add_method("make_node", |_lua, this, lua_path: String| {
            Ok(this.make_node(&PathBuf::from(lua_path)))
        });
        methods.add_method("abs_path", |_lua, this, ()| {
            Ok(this.path.to_string_lossy().to_string())
        });
        methods.add_method("nice_path", |_lua, this, ()| {
            Ok(this.nice_path().to_string_lossy().to_string())
        });
        methods.add_method("extension", |_lua, this, ()| {
            if let Some(ext) = this.path.extension() {
                Ok(ext.to_string_lossy().to_string())
            } else {
                Ok("".to_string())
            }
        });
        methods.add_method("change_ext", |_lua, this, new_ext: String| {
            let mut node = this.clone();
            node.change_ext(new_ext.as_str());
            Ok(node)
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
                    (Some(a), Some(Component::CurDir)) => comps.push(a),
                    (Some(_), Some(Component::ParentDir)) => {
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
        methods.add_method("name", |_lua, this: &Node, ()| {
            Ok(this
                .path
                .file_name()
                .map(|x| x.to_string_lossy().to_string()))
        });
        methods.add_method("basename", |_lua, this: &Node, ()| {
            Ok(this
                .path
                .with_extension("")
                .file_name()
                .map(|x| x.to_string_lossy().to_string()))
        });
        methods.add_method("is_dir", |_lua, this: &Node, ()| Ok(this.is_dir()));
        methods.add_method("is_file", |_lua, this: &Node, ()| Ok(this.is_file()));
        methods.add_method("read_link", |_lua, this: &Node, ()| Ok(this.read_link()));
        methods.add_method("canonicalize", |_lua, this: &Node, ()| {
            Ok(this.canonicalize())
        });
        methods.add_method("delete", |_lua, this: &Node, ()| {
            this.delete()
                .map_err(|x| LuaError::RuntimeError(x.to_string()))
        });
        methods.add_method("try_delete", |_lua, this: &Node, ()| {
            this.delete().or(Ok(()))
        });
        methods.add_method("mkdir", |_lua, this: &Node, ()| {
            this.mkdir()
                .map_err(|x| LuaError::RuntimeError(x.to_string()))
        });
        methods.add_method("read", |_lua, this: &Node, ()| {
            let mut content = Vec::new();
            std::fs::File::create(&this.path)?.read_to_end(&mut content)?;
            _lua.create_string(content)
        });
        methods.add_method("write", |_lua, this: &Node, content: LuaString| {
            std::fs::File::create(&this.path)?.write_all(content.as_bytes().deref())?;
            Ok(())
        });
    }
}

impl FromLua for Node {
    fn from_lua(value: Value, _lua: &Lua) -> mlua::Result<Self> {
        match value {
            Value::UserData(userdata) => Ok(userdata.borrow::<Node>()?.clone()),
            _ => Err(Error::FromLuaConversionError {
                from: value.type_name(),
                to: "Node".to_string(),
                message: None,
            }),
        }
    }
}
