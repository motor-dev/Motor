use mlua::{AnyUserData, UserData, UserDataFields, UserDataMethods, Value, FromLua};
use mlua::prelude::LuaError;
use crate::context::Context;
use crate::node::Node;
use super::{Task, TaskHandle};

impl UserData for TaskHandle {
    fn add_fields<'lua, F: UserDataFields<'lua, Self>>(fields: &mut F) {
        fields.add_field_function_get("driver", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            let context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;
            Ok(context.tasks[index].driver.clone())
        });
        fields.add_field_function_get("inputs", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            let context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;
            Ok(context.tasks[index].inputs.clone())
        });
        fields.add_field_function_get("outputs", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            let context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;
            Ok(context.tasks[index].outputs.clone())
        });
        fields.add_field_function_get("generator", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            let context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;
            Ok(context.tasks[index].generator.clone())
        });
        fields.add_field_function_get("group", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            let context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;
            Ok(context.tasks[index].group.clone())
        });
        fields.add_field_function_get("env", |_lua, this: AnyUserData| {
            let context = this.user_value::<AnyUserData>()?;
            let context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;
            Ok(context.tasks[index].env.clone())
        });
    }

    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_function_mut("add_input", |lua, (this, nodes): (AnyUserData, Value)| {
            let context = this.user_value::<AnyUserData>()?;
            let mut context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;

            let nodes = match &nodes {
                Value::Table(_) => Vec::<Node>::from_lua(nodes.clone(), lua)?,
                Value::UserData(d) => vec![d.borrow::<Node>()?.clone()],
                _ => return Err(LuaError::RuntimeError("inputs should be a node or a list of nodes".to_string())),
            };

            let mut dependencies = Vec::new();
            for node in &nodes {
                if let Some(&producer) = context.products.get(node.path()) {
                    dependencies.push((producer, index));
                }
            }

            context.add_dependencies(&dependencies, None)?;

            let hasher = &mut context.signatures[index];
            for input in &nodes {
                hasher.update(input.path().to_string_lossy().as_bytes());
            }
            let task = &mut context.tasks[index];
            task.inputs.extend(nodes);

            Ok(())
        });

        methods.add_function_mut("add_output", |lua, (this, nodes): (AnyUserData, Value)| {
            let context = this.user_value::<AnyUserData>()?;
            let mut context = context.borrow_mut::<Context>()?;
            let index = this.borrow::<TaskHandle>()?.0;

            let nodes = match &nodes {
                Value::Table(_) => Vec::<Node>::from_lua(nodes.clone(), lua)?,
                Value::UserData(d) => vec![d.borrow::<Node>()?.clone()],
                _ => return Err(LuaError::RuntimeError("outputs should be a node or a list of nodes".to_string())),
            };

            context.declare_products(&nodes, &mut Vec::new(), index, None)?;

            let hasher = &mut context.signatures[index];
            for output in &nodes {
                hasher.update(output.path().to_string_lossy().as_bytes());
            }
            let task = &mut context.tasks[index];
            task.outputs.extend(nodes);
            Ok(())
        });
    }
}


impl UserData for Task {
    fn add_fields<'lua, F: UserDataFields<'lua, Self>>(fields: &mut F) {
        fields.add_field_method_get("driver", |_lua, this| {
            Ok(this.driver.clone())
        });
        fields.add_field_method_get("inputs", |_lua, this| {
            Ok(this.inputs.clone())
        });
        fields.add_field_method_get("outputs", |_lua, this| {
            Ok(this.outputs.clone())
        });
        fields.add_field_method_get("generator", |_lua, this| {
            Ok(this.generator.clone())
        });
        fields.add_field_method_get("group", |_lua, this| {
            Ok(this.group.clone())
        });
        fields.add_field_method_get("env", |_lua, this| {
            Ok(this.env.clone())
        });
    }

    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_method(
            "run_command",
            |_lua, this, command: String| {
                Ok(this.run_command(command.as_str(), Vec::new()))
            },
        );
    }
}