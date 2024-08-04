use mlua::{MetaMethod, UserData, UserDataMethods, UserDataRef};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Component, Path, PathBuf};

#[derive(Clone, Serialize, Deserialize)]
pub(crate) struct Node {
    path: PathBuf,
}

impl Node {
    pub(crate) fn from(path: &PathBuf) -> Node {
        Node {
            path: normalize_path(path),
        }
    }

    pub(crate) fn path(&self) -> &PathBuf {
        &self.path
    }

    pub(crate) fn abspath(&self) -> &Path {
        self.path.as_path()
    }

    pub(crate) fn make_node(&self, path: &PathBuf) -> Node {
        let mut result = Node {
            path: self.path.clone(),
        };
        result.path.push(path);
        result
    }

    pub(crate) fn parent(self: &Self) -> Node {
        let mut result = Node {
            path: self.path.clone(),
        };
        result.path.pop();
        result
    }

    pub(crate) fn is_dir(self: &Self) -> bool {
        self.path.is_dir()
    }

    pub(crate) fn is_file(self: &Self) -> bool {
        self.path.is_file()
    }

    pub(crate) fn mkdir(self: &Self) -> std::io::Result<()> {
        fs::create_dir_all(&self.path)
    }
}

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
            Ok(this.abspath().to_string_lossy().to_string())
        });
        methods.add_method("make_node", |_lua, this, lua_path: String| {
            let path = Path::new(lua_path.as_str());
            let mut result = this.clone();
            result.path.push(path);
            Ok(result)
        });
        methods.add_method("abspath", |_lua, this, ()| {
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
                        return Err(mlua::Error::RuntimeError(String::from(
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
    }
}

fn normalize_path(path: &PathBuf) -> PathBuf {
    let mut components = path.components().peekable();
    let mut ret = if let Some(c @ Component::Prefix(..)) = components.peek().cloned() {
        components.next();
        PathBuf::from(c.as_os_str())
    } else {
        PathBuf::new()
    };

    for component in components {
        match component {
            Component::Prefix(..) => unreachable!(),
            Component::RootDir => {
                ret.push(component.as_os_str());
            }
            Component::CurDir => {}
            Component::ParentDir => {
                ret.pop();
            }
            Component::Normal(c) => {
                ret.push(c);
            }
        }
    }
    ret
}
