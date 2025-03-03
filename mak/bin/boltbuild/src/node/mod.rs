use crate::environment::MapValue;
use serde::{Deserialize, Serialize};
use std::ffi::OsStr;
use std::fmt::Display;
use std::fs;
use std::path::{Component, Path, PathBuf};

mod lua_binding;

#[derive(Clone, Serialize, Deserialize, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub(crate) struct Node {
    path: PathBuf,
}

impl Node {
    pub(crate) fn from(path: &Path) -> Node {
        Node {
            path: normalize_path(path),
        }
    }

    fn new() -> Node {
        Node {
            path: PathBuf::new(),
        }
    }

    pub(crate) fn path(&self) -> &PathBuf {
        &self.path
    }

    pub(crate) fn nice_path(&self) -> &Path {
        let path = self.path.as_path();
        path.strip_prefix(std::env::current_dir().unwrap())
            .unwrap_or(path)
    }

    pub(crate) fn abs_path(&self) -> &Path {
        self.path.as_path()
    }

    pub(crate) fn make_node(&self, path: &PathBuf) -> Node {
        let mut result = Node {
            path: self.path.clone(),
        };
        result.path.push(path);
        result.path = normalize_path(&result.path);
        result
    }

    pub(crate) fn parent(&self) -> Option<Node> {
        let mut result = Node {
            path: self.path.clone(),
        };
        if result.path.pop() {
            Some(result)
        } else {
            None
        }
    }

    pub(crate) fn is_dir(&self) -> bool {
        self.path.is_dir()
    }

    pub(crate) fn is_file(&self) -> bool {
        self.path.is_file()
    }

    pub(crate) fn read_link(&self) -> Self {
        let mut rel_path = self.path.clone();
        while let Ok(path) = fs::read_link(&rel_path) {
            rel_path.pop();
            rel_path.push(path);
        }
        Node::from(&rel_path)
    }

    pub(crate) fn canonicalize(&self) -> Self {
        let mut result = Self::new();
        for c in self.path.iter() {
            result.path.push(c);
            result = result.read_link();
        }
        result
    }

    pub(crate) fn mkdir(&self) -> std::io::Result<()> {
        fs::create_dir_all(&self.path)
    }

    pub(crate) fn delete(&self) -> std::io::Result<()> {
        fs::remove_file(&self.path)
    }

    pub(crate) fn name(&self) -> String {
        self.path
            .file_name()
            .unwrap_or(OsStr::new(""))
            .to_string_lossy()
            .to_string()
    }

    pub(crate) fn change_ext(&mut self, extension: &str) {
        self.path.set_extension(extension);
    }

    pub(crate) fn fix_case(&self) -> Node {
        let mut result = Node {
            path: PathBuf::new(),
        };
        for c in self.path.components() {
            result.path.push(c);
            if !result.path.exists() {
                result.path.pop();
                let content = result.path.read_dir();
                if let Ok(content) = content {
                    let mut found = false;
                    for entry in content.flatten() {
                        if entry.file_name().to_string_lossy().to_lowercase()
                            == c.as_os_str().to_string_lossy().to_lowercase()
                        {
                            result.path.push(entry.file_name());
                            found = true;
                            break;
                        }
                    }
                    if !found {
                        result.path.push(c);
                    }
                } else {
                    result.path.push(c);
                }
            }
        }
        result
    }
}

impl Display for Node {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.path.display())
    }
}

fn normalize_path(path: &Path) -> PathBuf {
    let mut components = path.components().peekable();
    let mut ret = if let Some(c @ Component::Prefix(..)) = components.peek().cloned() {
        components.next();
        PathBuf::from(c.as_os_str())
    } else {
        PathBuf::new()
    };

    for component in components {
        match component {
            Component::Prefix(_) => ret.push(component),
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

impl From<&Node> for MapValue {
    fn from(value: &Node) -> Self {
        MapValue::Node(value.clone())
    }
}

impl From<&Vec<Node>> for MapValue {
    fn from(value: &Vec<Node>) -> Self {
        MapValue::Vec(value.iter().map(|x| x.into()).collect::<Vec<MapValue>>())
    }
}
