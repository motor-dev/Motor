use crate::context::operations::Feature;
use crate::context::Context;
use crate::generator::Generator;
use mlua::prelude::{LuaError, LuaFunction, LuaResult, LuaValue};
use mlua::{AnyUserData, FromLua, Lua, UserData, UserDataMethods};
use std::sync::{Arc, Mutex};

fn partial_sort(
    mut features: Vec<String>,
    partial_order: &Vec<(String, String)>,
) -> LuaResult<Vec<String>> {
    for edge in partial_order {
        if !features.iter().any(|x| x.eq(&edge.0)) {
            return Err(LuaError::RuntimeError(format!(
                "Dependency on unknown feature {}",
                &edge.0
            )));
        }
        if !features.iter().any(|x| x.eq(&edge.1)) {
            return Err(LuaError::RuntimeError(format!(
                "Dependency on unknown feature {}",
                &edge.1
            )));
        }
    }

    let mut result = Vec::new();
    let mut edges = partial_order.clone();

    let mut roots = Vec::new();

    while let Some(index) = features
        .iter()
        .position(|x| !edges.iter().any(|edge| edge.1.eq(x)))
    {
        roots.push(features.remove(index));
    }
    roots.reverse();

    while let Some(root) = roots.pop() {
        while let Some(edge_index) = edges.iter().position(|x| x.0.eq(&root)) {
            let edge = edges.swap_remove(edge_index);
            if !edges.iter().any(|e| e.1.eq(&edge.1)) {
                if let Some(new_root) = features.iter().position(|x| x.eq(&edge.1)) {
                    roots.insert(0, features.swap_remove(new_root));
                }
            }
        }
        result.push(root);
    }

    if !edges.is_empty() {
        Err(LuaError::RuntimeError(format!(
            "Cycle detected in feature dependency:\n  {}",
            edges
                .iter()
                .map(|x| format!("{} -> {}", x.0, x.1))
                .collect::<Vec<_>>()
                .join("\n  ")
        )))
    } else {
        Ok(result)
    }
}

struct FeatureIndex(usize);

impl UserData for FeatureIndex {
    fn add_methods<M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_function(
            "set_run_after",
            |_lua, (this, predecessors): (AnyUserData, Vec<String>)| {
                let context = this.user_value::<AnyUserData>()?;
                let feature_index = this.borrow::<FeatureIndex>()?.0;
                let features = context.named_user_value::<Vec<AnyUserData>>(":features")?;
                context.borrow_mut_scoped::<Context, _>(|context| {
                let mut ordered_features = Vec::new();
                for f in features.iter() {
                    let feature_name = f.borrow::<Feature>()?.0.clone();
                    ordered_features.push(feature_name);
                }
                let name = &ordered_features[feature_index];
                let mut partial_order = context.partial_order.clone();
                for predecessor in predecessors {
                    partial_order.push((predecessor, name.clone()));
                }

                /* verify on the dummy data that all features exist and that there is no cycle */
                context.sorted_features = partial_sort(ordered_features, &partial_order)?;
                context.partial_order = partial_order;
                Ok::<_, LuaError>(())
            })??;
                Ok(this)
            },
        );
        methods.add_function(
            "set_run_before",
            |_lua, (this, successors): (AnyUserData, Vec<String>)| {
                let context = this.user_value::<AnyUserData>()?;
                let feature_index = this.borrow::<FeatureIndex>()?.0;
                let features = context.named_user_value::<Vec<AnyUserData>>(":features")?;
                context.borrow_mut_scoped::<Context, _>(|context| {
                let mut ordered_features = Vec::new();
                for f in features.iter() {
                    let feature_name = f.borrow::<Feature>()?.0.clone();
                    ordered_features.push(feature_name);
                }
                let name = &ordered_features[feature_index];
                let mut partial_order = context.partial_order.clone();
                for successor in successors {
                    partial_order.push((name.clone(), successor));
                }

                /* verify on the dummy data that all features exist and that there is no cycle */
                context.sorted_features = partial_sort(ordered_features, &partial_order)?;
                context.partial_order = partial_order;
                Ok::<_, LuaError>(())
            })??;
                Ok(this)
            },
        );
    }
}

impl UserData for Feature {}

pub(super) fn feature(
    lua: &Lua,
    (this, feature_names, name, method): (AnyUserData, LuaValue, String, LuaFunction),
) -> LuaResult<AnyUserData> {
    let feature_names = match &feature_names {
        LuaValue::String(s) => s
            .to_string_lossy()
            .split(',')
            .map(|x| x.trim().to_string())
            .collect(),
        LuaValue::Table(_) => Vec::<String>::from_lua(feature_names, lua)?,
        LuaValue::Nil => Vec::new(),
        _ => {
            return Err(LuaError::RuntimeError(
                "features should be a list of string or a single string".to_string(),
            ))
        }
    };

    let mut features = this.named_user_value::<Vec<AnyUserData>>(":features")?;
    for f in features.iter() {
        let feature_name = &f.borrow::<Feature>()?.0;
        if feature_name.eq(&name) {
            return Err(LuaError::RuntimeError(format!(
                "Feature {} already defined.",
                name
            )));
        }
    }

    this.borrow_mut_scoped::<Context, _>(|context| {
        context.sorted_features.push(name.clone());
    })?;

    let feature_index = lua.create_userdata(FeatureIndex(features.len()))?;

    let feature = lua.create_any_userdata(Feature(name, feature_names))?;
    feature.set_named_user_value(":call", method)?;
    features.push(feature);
    this.set_named_user_value(":features", features)?;

    feature_index.set_user_value(this)?;

    Ok(feature_index)
}

pub(super) fn post(_lua: &Lua, (this, generator): (&AnyUserData, &AnyUserData)) -> LuaResult<()> {
    if let Some((generator_name, features)) = this.borrow_scoped::<Context, _>(|owner| {
        let mut result_features = Vec::new();

        let generator_arc = generator.borrow_mut::<Arc<Mutex<Generator>>>()?;
        let mut generator = generator_arc.lock().unwrap();
        if generator.posted {
            return Ok(None);
        }
        generator.posted = true;
        if owner.in_post == 0 {
            return Err(LuaError::RuntimeError(format!(
                "Posting task generator {} outside of post",
                &generator.name
            )));
        }
        let mut available_features = Vec::new();
        for u in this.named_user_value::<Vec<AnyUserData>>(":features")? {
            let f = u.borrow::<Feature>()?;
            available_features.push((
                f.0.clone(),
                f.1.clone(),
                u.named_user_value::<LuaFunction>(":call")?,
            ));
        }
        for feature_name in &owner.sorted_features {
            let feature = available_features
                .iter()
                .find(|x| x.0.eq(feature_name))
                .unwrap();
            for f in &generator.features {
                if feature.1.iter().any(|x| x.eq(f)) {
                    result_features.push(feature.clone());
                    break;
                }
            }
        }
        Ok::<_, LuaError>(Some((generator.name.clone(), result_features)))
    })?? {
        for (name, _, callback) in features {
            this.borrow_mut_scoped::<Context, _>(|owner| {
                let depth = owner.in_post - 1;
                owner.logger.debug(
                    format!("{}posting {}:{}", " ".repeat(depth), generator_name, name).as_str(),
                );
                owner.in_post += 1;
            })?;
            let result = callback.call::<()>(generator);
            this.borrow_mut_scoped::<Context, _>(|owner| {
                owner.in_post -= 1;
            })?;
            result?;
        }
    }
    Ok(())
}
