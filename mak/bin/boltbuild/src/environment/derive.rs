use crate::environment::{FlatMap, OverlayMap, OverlayParent};
use mlua::prelude::LuaError;
use std::sync::{Arc, Mutex};

impl OverlayMap {
    pub(crate) fn derive(from: &Arc<Mutex<OverlayMap>>, index: usize) -> mlua::Result<Self> {
        if let OverlayParent::Leaf(_) = &from.lock().unwrap().parent {
            Err(LuaError::RuntimeError(
                "unable to derive from a task environment".to_string(),
            ))
        } else {
            Ok(Self {
                parent: OverlayParent::Current(from.clone()),
                index,
                environment: FlatMap::new(),
                sub_envs: Vec::new(),
            })
        }
    }

    pub(crate) fn derive_leaf(from: &Arc<Mutex<OverlayMap>>) -> mlua::Result<Self> {
        if let OverlayParent::Leaf(_) = &from.lock().unwrap().parent {
            Err(LuaError::RuntimeError(
                "unable to derive from a task environment".to_string(),
            ))
        } else {
            Ok(Self {
                parent: OverlayParent::Leaf(from.clone()),
                index: 0,
                environment: FlatMap::new(),
                sub_envs: Vec::new(),
            })
        }
    }

    pub(crate) fn derive_from_parent(from: &Arc<Mutex<OverlayMap>>, index: usize) -> Self {
        assert!(!matches!(
            from.lock().unwrap().parent,
            OverlayParent::Leaf(_)
        ));
        Self {
            parent: OverlayParent::Parent(from.clone()),
            index,
            environment: FlatMap::new(),
            sub_envs: Vec::new(),
        }
    }

    pub(crate) fn update_parent(&mut self, parents: &[Arc<Mutex<OverlayMap>>]) {
        match &self.parent {
            OverlayParent::Parent(env) => {
                let index = env.lock().unwrap().index;
                self.parent = OverlayParent::Parent(parents[index].clone());
            }
            OverlayParent::Leaf(env) => {
                let index = env.lock().unwrap().index;
                self.parent = OverlayParent::Leaf(parents[index].clone());
            }
            _ => (),
        }
    }
}
