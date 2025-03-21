use crate::environment::{FlatMap, OverlayMap, OverlayParent};
use mlua::prelude::LuaError;
use std::sync::{Arc, Mutex};

impl OverlayMap {
    pub(crate) fn derive(from: &Arc<Mutex<OverlayMap>>, index: usize) -> mlua::Result<Self> {
        let sub_envs = from.lock().unwrap().sub_envs.clone();
        if let OverlayParent::Leaf(_) = &from.lock().unwrap().parent {
            Err(LuaError::RuntimeError(
                "unable to derive from a task environment".to_string(),
            ))
        } else {
            Ok(Self {
                parent: OverlayParent::Current(from.clone()),
                index,
                environment: FlatMap::new(),
                sub_envs,
            })
        }
    }

    pub(crate) fn derive_leaf(from: &Arc<Mutex<OverlayMap>>) -> mlua::Result<Self> {
        let sub_envs = from.lock().unwrap().sub_envs.clone();
        if let OverlayParent::Leaf(_) = &from.lock().unwrap().parent {
            Err(LuaError::RuntimeError(
                "unable to derive from a task environment".to_string(),
            ))
        } else {
            Ok(Self {
                parent: OverlayParent::Leaf(from.clone()),
                index: 0,
                environment: FlatMap::new(),
                sub_envs,
            })
        }
    }

    pub(crate) fn derive_from_parent(
        from: &Arc<Mutex<OverlayMap>>,
        into: &mut Vec<Arc<Mutex<OverlayMap>>>,
        done: &mut Vec<Arc<Mutex<OverlayMap>>>,
    ) -> Arc<Mutex<OverlayMap>> {
        if let Some(index) = done.iter().position(|env| Arc::ptr_eq(env, from)) {
            into[index].clone()
        } else {
            assert!(!matches!(
                from.lock().unwrap().parent,
                OverlayParent::Leaf(_)
            ));
            let result = Arc::new(Mutex::new(Self {
                parent: OverlayParent::Parent(from.clone()),
                index: into.len(),
                environment: FlatMap::new(),
                sub_envs: Vec::new(),
            }));
            done.push(from.clone());
            into.push(result.clone());
            let sub_envs = from.lock().unwrap().sub_envs.clone();
            for env in &sub_envs {
                let sub_env = Self::derive_from_parent(&env.1.upgrade().unwrap(), into, done);
                let index = sub_env.lock().unwrap().index;
                result
                    .lock()
                    .unwrap()
                    .sub_envs
                    .push((index, Arc::downgrade(&sub_env)));
            }
            result
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
