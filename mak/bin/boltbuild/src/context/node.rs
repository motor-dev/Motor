use crate::command::SerializedHash;
use crate::context::Context;
use crate::environment::EnvironmentValue;
use crate::node::Node;
use blake3::Hasher;
use mlua::prelude::{LuaError, LuaResult};
use mlua::Lua;

pub(super) fn search(
    _lua: &Lua,
    this: &mut Context,
    (path, pattern, include_directories): (Node, String, Option<bool>),
) -> LuaResult<Vec<Node>> {
    let mut result = Vec::new();
    if path.is_dir() {
        let include_directories = include_directories.unwrap_or(false);
        let node = path.canonicalize();
        let path = node.path().join(&pattern);
        let search_string = &*path.to_string_lossy();
        let paths = glob::glob(&search_string)
            .map_err(|e| LuaError::RuntimeError(format!("pattern error: {}", e)))?;
        let mut hasher = Hasher::new();
        for path in paths.flatten() {
            hasher.update(path.as_os_str().as_encoded_bytes());
            if include_directories || !path.is_dir() {
                result.push(Node::from(&path));
            }
        }
        let mut store = true;
        let hash = hasher.finalize();
        for (prev_path, prev_pattern, prev_hash) in &this.output.stored_hash.glob_dependencies {
            if prev_path.path().eq(node.path()) & prev_pattern.eq(&pattern) {
                if !hash.eq(&prev_hash.0) {
                    todo!();
                }
                store = false;
            }
        }
        if store {
            this.output.stored_hash.glob_dependencies.push((
                node.clone(),
                pattern,
                SerializedHash(hash),
            ));
        }
    }
    result.sort();
    Ok(result)
}

pub(super) fn find_program(
    _lua: &Lua,
    this: &mut Context,
    (program, paths): (String, Option<Vec<Node>>),
) -> LuaResult<Option<Node>> {
    let paths = paths.unwrap_or_else(|| {
        let paths = this.options.get_value("path");
        if let Some(paths) = paths {
            paths
                .into_list()
                .into_iter()
                .flat_map(|x| x.as_node(&this.path))
                .collect()
        } else {
            Vec::new()
        }
    });
    let suffix = this
        .options
        .get_value("exe_suffix")
        .unwrap_or(EnvironmentValue::String("".to_string()))
        .as_string();
    let pattern = program + suffix.as_str();

    for path in paths {
        let path = path.canonicalize();
        let executable = path.path().join(&pattern);
        let mut hasher = Hasher::new();
        if executable.is_file() {
            hasher.update(executable.as_os_str().as_encoded_bytes());
            this.output.stored_hash.glob_dependencies.push((
                path.clone(),
                pattern.clone(),
                SerializedHash(hasher.finalize()),
            ));
            return Ok(Some(Node::from(&executable)));
        } else {
            this.output.stored_hash.glob_dependencies.push((
                path.clone(),
                pattern.clone(),
                SerializedHash(hasher.finalize()),
            ));
        }
    }
    Ok(None)
}
