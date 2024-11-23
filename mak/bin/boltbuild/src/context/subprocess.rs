use crate::context::Context;
use mlua::prelude::LuaValue;
use mlua::Error as LuaError;
use mlua::Result as LuaResult;
use mlua::{AnyUserData, Lua, MetaMethod, UserData, UserDataMethods};
use std::io::{Read, Write};
use std::mem::swap;
use std::process::Stdio;

pub(super) struct Process(std::process::Child);

pub(super) fn popen(_lua: &Lua, this: &mut Context, command: Vec<LuaValue>) -> LuaResult<Process> {
    let mut cmd = Vec::new();
    this.logger.info(
        format!(
            "running command {}",
            command
                .iter()
                .map(|x| x.to_string().unwrap())
                .collect::<Vec<String>>()
                .join(" ")
        )
        .as_str(),
    );
    for x in command {
        cmd.push(x.to_string()?);
    }
    Process::create(&cmd)
}

impl Process {
    pub(crate) fn create(command: &[String]) -> LuaResult<Self> {
        let process = std::process::Command::new(&command[0])
            .args(&command[1..command.len()])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| LuaError::RuntimeError(format!("Process creation error error: {}", e)))?;
        Ok(Self(process))
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

impl Drop for Process {
    fn drop(&mut self) {
        self.0.wait().unwrap();
    }
}

impl UserData for Process {
    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_method_mut("communicate", |_lua, this, input: Option<String>| {
            std::thread::scope(|scope| {
                let mut stdout = None;
                swap(&mut stdout, &mut this.0.stdout);
                let mut stderr = None;
                swap(&mut stderr, &mut this.0.stderr);

                let stdout_reader = scope.spawn(move || {
                    let mut output = Vec::new();
                    stdout.as_mut().unwrap().read_to_end(&mut output).unwrap();
                    output
                });
                let stderr_reader = scope.spawn(move || {
                    let mut output = Vec::new();
                    stderr.as_mut().unwrap().read_to_end(&mut output).unwrap();
                    output
                });
                if let Some(input) = input {
                    this.0
                        .stdin
                        .as_mut()
                        .unwrap()
                        .write_all(input.as_bytes())
                        .unwrap();
                }
                this.0.stdin = None;
                let exit_status = this
                    .0
                    .wait()
                    .map_err(|x| LuaError::RuntimeError(format!("Subprocess error `{}`", x)))?;
                let stdout = stdout_reader.join().unwrap();
                let stdout = String::from_utf8(stdout)
                    .map_err(|x| LuaError::RuntimeError(format!("Utf8 decode error `{}`", x)))?;
                let stderr = stderr_reader.join().unwrap();
                let stderr = String::from_utf8(stderr)
                    .map_err(|x| LuaError::RuntimeError(format!("Utf8 decode error `{}`", x)))?;

                Ok((
                    exit_status.success(),
                    Out::new(Some(stdout)),
                    Out::new(Some(stderr)),
                ))
            })
        })
    }
}

impl UserData for Out {
    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_meta_method(MetaMethod::Add, |_lua, this, other: AnyUserData| {
            let other = other.borrow::<Out>()?;
            Ok(Out([this.0.as_str(), other.0.as_str()].join(""), this.1))
        });
        methods.add_meta_method(MetaMethod::ToString, |_lua, this, ()| Ok(this.0.clone()));
        methods.add_function_mut("lines", |lua, this: AnyUserData| {
            {
                let _ = this.borrow::<Out>()?;
            }
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
            })?
            .bind(this)
        })
    }
}
