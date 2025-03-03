use super::{Task, TaskHandle};
use crate::context::Context;
use crate::node::Node;
use mlua::prelude::LuaError;
use mlua::{AnyUserData, FromLua, UserData, UserDataFields, UserDataMethods, Value};

impl UserData for TaskHandle {
    fn add_fields<F: UserDataFields<Self>>(fields: &mut F) {
        fields.add_field_function_get("driver", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;
                Ok(context.tasks[index].driver.clone())
            })?
        });
        fields.add_field_function_get("inputs", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;
                Ok(context.tasks[index].inputs.clone())
            })?
        });
        fields.add_field_function_get("outputs", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;
                Ok(context.tasks[index].outputs.clone())
            })?
        });
        fields.add_field_function_get("generator", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;
                Ok(context.tasks[index].generator.clone())
            })?
        });
        fields.add_field_function_get("group", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;
                Ok(context.tasks[index].group.clone())
            })?
        });
        fields.add_field_function_get("env", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;
                Ok(context.tasks[index].env.clone())
            })?
        });
    }

    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_function_mut("add_input", |lua, (this, nodes): (AnyUserData, Value)| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;

                let nodes = match &nodes {
                    Value::Table(_) => Vec::<Node>::from_lua(nodes.clone(), lua)?,
                    Value::UserData(d) => vec![d.borrow::<Node>()?.clone()],
                    _ => {
                        return Err(LuaError::RuntimeError(
                            "inputs should be a node or a list of nodes".to_string(),
                        ))
                    }
                };

                context.add_inputs(index, &nodes)?;

                let hasher = &mut context.signatures[index];
                for input in &nodes {
                    hasher.update(input.path().to_string_lossy().as_bytes());
                }
                let task = &mut context.tasks[index];
                task.inputs.extend(nodes);

                Ok(())
            })?
        });

        methods.add_function_mut("add_output", |lua, (this, nodes): (AnyUserData, Value)| {
            let context = this.user_value::<AnyUserData>()?;
            context.borrow_mut_scoped::<Context, _>(|context| {
                let index = this.borrow::<TaskHandle>()?.0;

                let nodes = match &nodes {
                    Value::Table(_) => Vec::<Node>::from_lua(nodes.clone(), lua)?,
                    Value::UserData(d) => vec![d.borrow::<Node>()?.clone()],
                    _ => {
                        return Err(LuaError::RuntimeError(
                            "outputs should be a node or a list of nodes".to_string(),
                        ))
                    }
                };

                context.add_outputs(index, &nodes)?;

                let hasher = &mut context.signatures[index];
                for output in &nodes {
                    hasher.update(output.path().to_string_lossy().as_bytes());
                }
                let task = &mut context.tasks[index];
                task.outputs.extend(nodes);
                Ok(())
            })?
        });

        methods.add_function_mut(
            "set_run_before",
            |_lua, (this, other): (AnyUserData, AnyUserData)| {
                let context = this.user_value::<AnyUserData>()?;
                context.borrow_mut_scoped::<Context, _>(|context| {
                    let index = this.borrow::<TaskHandle>()?.0;
                    let other = other.borrow::<TaskHandle>()?.0;

                    context.add_dependencies(vec![(index, other, "run before".to_string())])
                })?
            },
        );

        methods.add_function_mut(
            "set_run_after",
            |_lua, (this, other): (AnyUserData, AnyUserData)| {
                let context = this.user_value::<AnyUserData>()?;
                context.borrow_mut_scoped::<Context, _>(|context| {
                    let index = this.borrow::<TaskHandle>()?.0;
                    let other = other.borrow::<TaskHandle>()?.0;

                    context.add_dependencies(vec![(other, index, "run after".to_string())])
                })?
            },
        );
    }
}

impl UserData for Task {
    fn add_fields<F: UserDataFields<Self>>(fields: &mut F) {
        fields.add_field_method_get("driver", |_lua, this| Ok(this.driver.clone()));
        fields.add_field_method_get("inputs", |_lua, this| Ok(this.inputs.clone()));
        fields.add_field_method_get("outputs", |_lua, this| Ok(this.outputs.clone()));
        fields.add_field_method_get("generator", |_lua, this| Ok(this.generator.clone()));
        fields.add_field_method_get("group", |_lua, this| Ok(this.group.clone()));
        fields.add_field_method_get("env", |_lua, this| Ok(this.env.clone()));
    }

    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_method("run_command", |_lua, this, command: String| {
            Ok(this.run_command(command.as_str(), Vec::new()))
        });
    }
}
