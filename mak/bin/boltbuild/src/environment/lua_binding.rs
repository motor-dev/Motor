use crate::environment::{FlatMap, MapValue, OverlayMap, OverlayParent};
use mlua::{AnyUserData, Lua, MetaMethod, UserData, UserDataMethods, Value};
use std::sync::{Arc, Mutex, Weak};

impl FlatMap {
    pub(crate) fn get_into_lua(&mut self, lua: &Lua, key: &str) -> mlua::Result<Value> {
        self.used_keys.insert(key.to_string());
        match self.values.get(key) {
            None => Ok(mlua::Nil),
            Some(v) => v.get_into_lua(&[], lua),
        }
    }

    pub(crate) fn set(&mut self, name: &str, value: MapValue) {
        self.values.insert(name.into(), value);
    }
}

impl OverlayMap {
    fn make_list(&mut self, key: &str) -> Vec<MapValue> {
        self.environment.used_keys.insert(key.to_string());
        match self.environment.values.get(key) {
            None => match &self.parent {
                OverlayParent::None => Vec::new(),
                OverlayParent::Current(e) | OverlayParent::Parent(e) | OverlayParent::Leaf(e) => {
                    e.lock().unwrap().make_list(key)
                }
            },
            Some(v) => match v {
                MapValue::Vec(v) => v.clone(),
                _ => vec![v.clone()],
            },
        }
    }

    fn get_into_lua<'a, 'lua>(&'a mut self, lua: &'lua Lua, key: &'a str) -> mlua::Result<Value> {
        self.environment.used_keys.insert(key.to_string());
        self.get_into_lua_with_envs(&self.sub_envs, lua, key)
    }

    fn get_into_lua_with_envs<'a, 'lua>(
        &'a self,
        sub_envs: &[(usize, Weak<Mutex<OverlayMap>>)],
        lua: &'lua Lua,
        key: &'a str,
    ) -> mlua::Result<Value> {
        match self.environment.values.get(key) {
            None => match &self.parent {
                OverlayParent::None => Ok(mlua::Nil),
                OverlayParent::Current(e) | OverlayParent::Parent(e) | OverlayParent::Leaf(e) => {
                    e.lock().unwrap().get_into_lua_with_envs(sub_envs, lua, key)
                }
            },
            Some(v) => v.get_into_lua(sub_envs, lua),
        }
    }

    pub(crate) fn set(&mut self, name: &str, value: MapValue) {
        self.environment.values.insert(name.into(), value);
    }
}

impl UserData for FlatMap {
    fn add_methods<'lua, M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_meta_method_mut(MetaMethod::Index, |lua, this, key: String| {
            this.get_into_lua(lua, key.as_str())
        });
    }
}

impl UserData for OverlayMap {
    fn add_methods<'lua, M: UserDataMethods<Self>>(methods: &mut M) {
        methods.add_function(
            "append",
            |_lua, (this, key, value): (AnyUserData, String, Value)| {
                let (mut original_value, mut sub_envs) = {
                    let value = this.borrow::<Arc<Mutex<OverlayMap>>>()?;
                    let mut this = value.lock().unwrap();
                    (this.make_list(key.as_str()), this.sub_envs.clone())
                };
                let value = MapValue::from_lua(&value, &mut sub_envs)?;
                if value.is_list() {
                    original_value.extend(value.into_list());
                } else {
                    original_value.push(value);
                }
                this.borrow_mut::<Arc<Mutex<OverlayMap>>>()?
                    .lock()
                    .unwrap()
                    .set(key.as_str(), MapValue::Vec(original_value));
                Ok(())
            },
        );
        methods.add_meta_method_mut(MetaMethod::Index, |lua, this, key: String| {
            this.get_into_lua(lua, key.as_str())
        });
        methods.add_meta_function(
            MetaMethod::NewIndex,
            |_lua, (this, key, value): (AnyUserData, String, Value)| {
                let mut sub_envs = this
                    .borrow_mut::<Arc<Mutex<OverlayMap>>>()?
                    .lock()
                    .unwrap()
                    .sub_envs
                    .clone();
                let value = MapValue::from_lua(&value, &mut sub_envs)?;
                {
                    let arc = this.borrow::<Arc<Mutex<OverlayMap>>>()?;
                    let mut this = arc.lock().unwrap();
                    this.set(key.as_str(), value);
                    this.sub_envs = sub_envs;
                }
                Ok(())
            },
        );
        methods.add_meta_method_mut(MetaMethod::ToString, |_lua, this, ()| {
            Ok(format!("env {}", this.index))
        });
    }
}
