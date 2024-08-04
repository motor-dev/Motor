use mlua::{AnyUserData, MetaMethod, UserData, UserDataMethods};
use mlua::Result as LuaResult;
use mlua::Error as LuaError;

pub(crate) struct Popen(subprocess::Popen);

impl Popen {
    pub(crate) fn create(command: &Vec<String>) -> LuaResult<Self> {
        Ok(Self(subprocess::Popen::create(
            command,
            subprocess::PopenConfig {
                stdin: subprocess::Redirection::Pipe,
                stdout: subprocess::Redirection::Pipe,
                stderr: subprocess::Redirection::Pipe,
                ..subprocess::PopenConfig::default()
            },
        ).map_err(|e| LuaError::RuntimeError(format!("Popen error: {}", e)))?))
    }
}

struct Out(String, Option<usize>);

impl Out {
    fn new(from: Option<String>) -> Self {
        match from {
            Some(x) => Self(x, Some(0)),
            None => Self("".to_string(), None),
        }
    }
}

impl Drop for Popen {
    fn drop(&mut self) {
        if self.0.poll().is_none() {
            self.0.terminate().unwrap();
        }
    }
}

impl UserData for Popen {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_method_mut("communicate", |_lua, this, input: Option<String>| {
            let result = this.0.communicate(input.as_ref().and_then(|x| Some(x.as_str())).or_else(|| { Some("") }))?;
            let exit_status = this.0.wait().map_err(|x| LuaError::RuntimeError(format!("Subprocess error `{}`", x)))?;
            Ok((exit_status.success(), Out::new(result.0), Out::new(result.1)))
        })
    }
}


impl UserData for Out {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_method(MetaMethod::Concat, |_lua, this, other: AnyUserData| {
            let other = other.borrow::<Out>()?;
            Ok(Out([this.0.as_str(), other.0.as_str()].join(""), this.1))
        });
        methods.add_function_mut("lines", |lua, this: AnyUserData| {
            { let _ = this.borrow::<Out>()?; }
            lua.create_function(|_lua, arg: AnyUserData| {
                let mut this = arg.borrow_mut::<Out>()?;
                match this.1 {
                    Some(index) => {
                        let end = this.0[index..].find('\n');
                        if let Some(end) = end {
                            let result = this.0[index..index + end].to_string();
                            this.1 = Some(index + end + 1);
                            Ok(Some(result))
                        } else {
                            let result = this.0[index..].to_string();
                            this.1 = None;
                            Ok(Some(result))
                        }
                    }
                    None => Ok(None),
                }
            })?.bind(this)
        })
    }
}

