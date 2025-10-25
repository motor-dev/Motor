use crate::context::operations::DeclaredCommand;
use crate::context::{Context, TOOLS_DIR, TOOLS_PATH};
use crate::environment::OverlayMap;
use crate::node::Node;
use include_dir::Dir;
use mlua::prelude::{LuaError, LuaResult, LuaString, LuaValue};
use mlua::{AnyUserData, FromLua, Lua, UserData};
use std::mem::swap;
use std::ops::Deref;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

impl UserData for DeclaredCommand {}

pub(super) fn recurse(lua: &Lua, args: (AnyUserData, LuaString)) -> LuaResult<()> {
    let path = args.1.to_str()?;
    let (old_path, script) = args.0.borrow_mut_scoped::<Context, _>(|this| {
        let mut script = this.path.make_node(&PathBuf::from(path.deref()));
        if script.is_dir() {
            let mut script_path = PathBuf::from(&this.spec.function);
            script_path.set_extension("lua");
            script = script.make_node(&script_path);
        }
        if !script.is_file() {
            Err(LuaError::RuntimeError(format!(
                "could not locate script `{:?}`",
                script.nice_path()
            )))
        } else {
            let mut old_path = script.parent().unwrap();
            swap(&mut old_path, &mut this.path);
            this.output
                .stored_hash
                .file_dependencies
                .push(script.path().clone());
            Ok((old_path, script))
        }
    })??;
    let result: LuaResult<()> = lua.load(script.nice_path()).call(&args.0);
    args.0.borrow_mut_scoped::<Context, _>(|this| {
        this.path = old_path;
    })?;
    result
}

pub(super) fn load_tool(
    lua: &Lua,
    (this, tool, again): (AnyUserData, String, Option<bool>),
) -> LuaResult<()> {
    let paths = this.borrow_scoped::<Context, _>(|this| {
        Ok::<_, LuaError>(this.options.get_node_vec("tools_dir", &this.path))
    })??;
    let tool_file = tool.to_owned() + ".lua";

    for node in &paths {
        let node = node.make_node(&PathBuf::from(&tool_file));
        if node.is_file() {
            let do_run = this.borrow_mut_scoped::<Context, _>(|this| {
                if !this.output.tools.iter().any(|x| x == &node) {
                    this.output.tools.push(node.clone());
                    true
                } else {
                    again.is_some() && again.unwrap()
                }
            })?;

            if do_run {
                lua.load(node.nice_path()).call::<()>(this)?;
            }
            return Ok(());
        }
    }

    if let Some(file) = TOOLS_DIR.get_file(&tool_file) {
        let do_run = this.borrow_mut_scoped::<Context, _>(|this| {
            let tool_node = Node::from(&PathBuf::from(&tool_file));
            if !this.output.tools.iter().any(|x| x == &tool_node) {
                this.output.tools.push(tool_node);
                true
            } else {
                again.is_some() && again.unwrap()
            }
        })?;
        if do_run {
            lua.load(file.contents())
                .set_name(format!(
                    "@{}",
                    PathBuf::from(TOOLS_PATH)
                        .join("tools")
                        .join(&tool_file)
                        .display()
                ))
                .call::<()>(this)?;
        }
        return Ok(());
    }

    let mut builtin_tools = Vec::new();
    fn walk(dir: &Dir, tools: &mut Vec<String>) {
        for entry in dir.files() {
            tools.push(entry.path().with_extension("").to_str().unwrap().to_owned());
        }
        for entry in dir.dirs() {
            walk(entry, tools);
        }
    }
    walk(&TOOLS_DIR, &mut builtin_tools);

    this.borrow_mut_scoped::<Context, _>(|this| {
        Err(LuaError::RuntimeError(
            format!("could not locate tool {}\nsearch paths:\n  {}\nbuilt-in tools:\n  {}\ncurrent directory:\n  {}\n",
                    tool,
                    paths.iter().map(|x| x.to_string()).collect::<Vec<String>>().join("\n  "),
                    builtin_tools.join("\n  "),
                    this.path
            )))
    })?
}

pub(super) fn declare_command(
    lua: &Lua,
    this: &mut Context,
    args: (String, String, LuaValue, Option<bool>),
) -> LuaResult<DeclaredCommand> {
    let mut envs = Vec::new();
    if args.2.is_table() {
        for env in Vec::<AnyUserData>::from_lua(args.2, lua)? {
            envs.push(
                env.borrow::<Arc<Mutex<OverlayMap>>>()?
                    .lock()
                    .unwrap()
                    .index,
            );
        }
    } else if args.2.is_nil() {
        envs.push(this.environment.lock().unwrap().index);
    } else if let Some(env) = args.2.as_userdata() {
        envs.push(
            env.borrow::<Arc<Mutex<OverlayMap>>>()?
                .lock()
                .unwrap()
                .index,
        );
    } else {
        return Err(LuaError::RuntimeError(
            "invalid value for environment".to_string(),
        ));
    }
    let path = this.declare_command(args.0.as_str(), args.1.as_str(), envs, args.3.unwrap_or(false))?;
    Ok(DeclaredCommand { path })
}

pub(super) fn chain_command(
    _lua: &Lua,
    this: &mut Context,
    args: (AnyUserData, String, String),
) -> LuaResult<DeclaredCommand> {
    let path = args.0.borrow_mut::<DeclaredCommand>()?;
    let sub_path = this.declare_chain(path.deref(), args.1.as_str(), args.2.as_str())?;
    Ok(DeclaredCommand { path: sub_path })
}
