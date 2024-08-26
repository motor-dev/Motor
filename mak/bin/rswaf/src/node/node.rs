use super::Node;

use std::fmt::Display;
use std::fs;
use std::path::{Component, Path, PathBuf};

impl Node {
    pub(crate) fn from(path: &PathBuf) -> Node {
        Node {
            path: normalize_path(path),
        }
    }

    pub(crate) fn path(&self) -> &PathBuf {
        &self.path
    }

    pub(crate) fn abs_path(&self) -> &Path {
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

    pub(crate) fn delete(self: &Self) -> std::io::Result<()> {
        fs::remove_file(&self.path)
    }
}

impl Display for Node {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.path.to_string_lossy().to_string())
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
