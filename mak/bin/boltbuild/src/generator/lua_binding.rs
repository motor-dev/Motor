use super::Generator;
use crate::command::SerializedHash;
use crate::context::Context;
use crate::environment::ReadWriteEnvironment;
use crate::node::Node;
use crate::task::{Task, TaskHandle};
use mlua::prelude::{LuaError, LuaValue};
use mlua::{AnyUserData, FromLua, MetaMethod, UserData, UserDataFields, UserDataMethods, Value};
use std::ops::Deref;
use std::sync::{Arc, Mutex};

impl UserData for Generator {
    fn add_fields<F: UserDataFields<Self>>(fields: &mut F) {
        fields.add_field_method_get("name", |_lua, this| Ok(this.name.clone()));
        fields.add_field_method_get("group", |_lua, this| Ok(this.group.clone()));
        fields.add_field_method_get("env", |_lua, this| Ok(this.env.clone()));
        fields.add_field_method_get("features", |_lua, this| Ok(this.features.clone()));
    }

    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_meta_function_mut(
            MetaMethod::NewIndex,
            |_lua, (context, name, value): (AnyUserData, String, LuaValue)| {
                context.set_named_user_value(name.as_str(), value)
            },
        );

        methods.add_meta_function_mut(
            MetaMethod::Index,
            |_lua, (generator, name): (AnyUserData, String)| {
                let result = generator.named_user_value::<LuaValue>(name.as_str())?;
                if result.is_nil() {
                    Err(LuaError::RuntimeError(format!(
                        "Context does not have a user value `{}`",
                        name
                    )))
                } else {
                    Ok(result)
                }
            },
        );

        methods.add_function_mut(
            "has_property",
            |_lua, (generator, name): (AnyUserData, String)| {
                let result = generator.named_user_value::<LuaValue>(name.as_str())?;
                Ok(!result.is_nil())
            },
        );

        methods.add_function_mut("declare_task", |lua, (generator, driver, inputs, outputs, env): (AnyUserData, String, Value, Value, Option<AnyUserData>)| {
            let inputs = match &inputs {
                Value::Nil => Vec::new(),
                Value::Table(_) => Vec::<Node>::from_lua(inputs, lua)?,
                Value::UserData(d) => vec![d.borrow::<Node>()?.clone()],
                _ => return Err(LuaError::RuntimeError("inputs should be a node or a list of nodes".to_string())),
            };
            let outputs = match &outputs {
                Value::Nil => Vec::new(),
                Value::Table(_) => Vec::<Node>::from_lua(outputs, lua)?,
                Value::UserData(d) => vec![d.borrow::<Node>()?.clone()],
                _ => return Err(LuaError::RuntimeError("outputs should be a node or a list of nodes".to_string())),
            };

            let context = generator.named_user_value::<AnyUserData>(":context")?;
            let handle = context.borrow_mut_scoped::<Context, _>(|context| {
                let generator = generator.borrow::<Arc<Mutex<Generator>>>()?;
                let generator = generator.lock().unwrap();
                let group = generator.group.clone();
                if !context.output.drivers.contains_key(&driver) {
                    return Err(LuaError::RuntimeError(format!("Context has no driver for tasks of type `{}`", &driver)));
                }
                let task_index = context.tasks.len();

                let from_env = if let Some(env) = env {
                    env.borrow::<Arc<Mutex<ReadWriteEnvironment>>>()?.deref().clone()
                } else {
                    generator.env.clone()
                };

                let env = Arc::new(Mutex::new(ReadWriteEnvironment::derive_leaf(&from_env)?));
                let task = Task {
                    driver,
                    generator: generator.name.clone(),
                    group,
                    env,
                    inputs,
                    outputs,
                    predecessors: Vec::new(),
                    successors: Vec::new(),
                    signature: SerializedHash(blake3::hash(&[])),
                };

                let mut dependencies = Vec::new();
                for node in &task.inputs {
                    if let Some(&producer) = context.products.get(node.path()) {
                        dependencies.push((producer, task_index, format!("dependency on {}", node)));
                    }
                }

                for (predecessor, successor) in &context.driver_order {
                    if predecessor.eq(&task.driver) {
                        if let Some(tasks) = context.driver_tasks.get(successor) {
                            for &task in tasks {
                                dependencies.push((task_index, task, format!("dependency {} -> {}", predecessor, successor)));
                            }
                        }
                    } else if successor.eq(&task.driver) {
                        if let Some(tasks) = context.driver_tasks.get(predecessor) {
                            for &task in tasks {
                                dependencies.push((task, task_index, format!("dependency {} -> {}", predecessor, successor)));
                            }
                        }
                    }
                }

                let mut hasher = blake3::Hasher::new();
                hasher.update(task.driver.as_bytes());
                hasher.update(task.generator.as_bytes());
                hasher.update(task.group.as_bytes());
                for input in &task.inputs {
                    hasher.update(input.path().to_string_lossy().as_bytes());
                }
                for output in &task.outputs {
                    hasher.update(output.path().to_string_lossy().as_bytes());
                }

                /* side effects start here. The function is not allowed to fail if declare_product is successful. */
                context.declare_products(&task.outputs, dependencies, task_index, Some(&task))?;
                context.driver_tasks.entry(task.driver.clone()).or_default().push(task_index);

                context.tasks.push(task);
                context.signatures.push(hasher);
                Ok(task_index)
            })??;

            let result = lua.create_userdata(TaskHandle(handle))?;
            result.set_user_value(context)?;
            Ok(result)
        })
    }
}
