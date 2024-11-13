use std::mem::swap;
use std::ops::Deref;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use mlua::{AnyUserData, Lua, FromLua, UserData};
use mlua::prelude::{LuaError, LuaResult, LuaString, LuaValue};
use crate::context::{Context, TOOLS_DIR};
use crate::context::operations::DeclaredCommand;
use crate::environment::ReadWriteEnvironment;
use crate::node::Node;
use crate::options::Options;

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
        let mut old_path = script.parent();
        swap(&mut old_path, &mut this.path);
        this.output
            .stored_hash
            .file_dependencies
            .push(script.path().clone());
        (old_path, script)
    })?;
    let result: LuaResult<()> = lua.load(script.abs_path()).call(&args.0);
    args.0.borrow_mut_scoped::<Context, _>(|this| {
        this.path = old_path;
    })?;
    result
}

pub(super) fn load_tool(lua: &Lua, (this, tool, again): (AnyUserData, String, Option<bool>)) -> LuaResult<()> {
    let paths = this.borrow_mut_scoped::<Context, _>(|this| {
        let mut nodes = Vec::new();
        for x in match &mut this.options {
            Options::Environment(e) => e.get_into_list("tools_dir"),
            Options::CommandLineParser(cl) => {
                let cl = cl.lock().unwrap();
                cl.get_value("tools_dir")?.into_list()
            }
        } {
            nodes.push(x.as_node(&this.path)?);
        }
        Ok::<_, LuaError>(nodes)
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
                lua.load(node.abs_path()).call::<()>(this)?;
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
            lua.load(file.contents()).set_name(tool_file).call::<()>(this)?;
        }
        return Ok(());
    }


    this.borrow_mut_scoped::<Context, _>(|this| {
        Err(LuaError::RuntimeError(
            format!("could not locate tool {}\nsearch paths:\n  {}\ncurrent directory:\n  {}\n",
                    tool,
                    paths.iter().map(|x| x.to_string()).collect::<Vec<String>>().join(",\n  "),
                    this.path
            )))
    })?
}

pub(super) fn declare_command(lua: &Lua, this: &mut Context, args: (String, String, LuaValue)) -> LuaResult<DeclaredCommand> {
    let mut envs = Vec::new();
    if args.2.is_table() {
        for env in Vec::<AnyUserData>::from_lua(args.2, lua)? {
            envs.push(
                env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?
                    .lock()
                    .unwrap()
                    .index,
            );
        }
    } else {
        let env = args
            .2
            .as_userdata()
            .unwrap()
            .borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?;
        envs.push(env.lock().unwrap().index);
    }
    let path = this.declare_command(args.0.as_str(), args.1.as_str(), envs)?;
    Ok(DeclaredCommand { path })
}

pub(super) fn chain_command(_lua: &Lua, this: &mut Context, args: (AnyUserData, String, String)) -> LuaResult<DeclaredCommand> {
    let path = args.0.borrow_mut::<DeclaredCommand>()?;
    let sub_path =
        this.declare_chain(path.deref(), args.1.as_str(), args.2.as_str())?;
    Ok(DeclaredCommand { path: sub_path })
}
