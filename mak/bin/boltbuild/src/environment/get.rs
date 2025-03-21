use crate::environment::{FlatMap, MapValue, OverlayMap, OverlayParent};
use crate::node::Node;
use std::sync::{Mutex, Weak};

mod private {
    pub(crate) trait RawGet {
        fn get_raw(&self, key: &str) -> super::MapValue;
    }
    pub(crate) trait Get: RawGet {
        fn get(&mut self, key: &str) -> super::MapValue;
    }
}

pub(crate) trait Lookup: private::Get {
    fn get_string(&mut self, key: &str) -> String {
        self.get(key).as_string(&[])
    }

    fn get_string_vec(&mut self, key: &str) -> Vec<String> {
        self.get(key).as_string_vec(&[])
    }

    fn get_node_vec(&mut self, key: &str, current_dir: &Node) -> Vec<Node> {
        self.get(key).as_node_vec(current_dir)
    }

    fn get_integer(&mut self, key: &str) -> i64 {
        self.get(key).as_int()
    }
}

pub(crate) trait Hash: private::RawGet {
    fn hash_key_with_envs(
        &self,
        key: &str,
        hasher: &mut blake3::Hasher,
        sub_envs: &[(usize, Weak<Mutex<OverlayMap>>)],
    );
    fn hash(&self, keys: &[String], hasher: &mut blake3::Hasher);
}

pub(crate) trait RawLookup: private::RawGet {
    fn is_none(&self, key: &str) -> bool {
        self.get_raw(key).is_none()
    }

    fn is_list(&self, key: &str) -> bool {
        self.get_raw(key).is_list()
    }

    fn get_string_raw(&self, key: &str) -> String {
        self.get_raw(key).as_string(&[])
    }

    fn get_string_vec_raw(&self, key: &str) -> Vec<String> {
        self.get_raw(key).as_string_vec(&[])
    }

    fn get_node(&self, key: &str, current_dir: &Node) -> Option<Node> {
        self.get_raw(key).as_node(current_dir)
    }

    fn get_integer_raw(&self, key: &str) -> i64 {
        self.get_raw(key).as_int()
    }

    fn get_bool_raw(&self, key: &str) -> Option<bool> {
        self.get_raw(key).as_bool()
    }
}

impl private::RawGet for FlatMap {
    fn get_raw(&self, key: &str) -> MapValue {
        match self.values.get(key) {
            None => MapValue::None,
            Some(v) => v.clone(),
        }
    }
}

impl private::Get for FlatMap {
    fn get(&mut self, key: &str) -> MapValue {
        use private::RawGet;
        self.used_keys.insert(key.to_string());
        self.get_raw(key)
    }
}

impl RawLookup for FlatMap {}

impl Lookup for FlatMap {}

impl Hash for FlatMap {
    fn hash_key_with_envs(
        &self,
        key: &str,
        hasher: &mut blake3::Hasher,
        sub_envs: &[(usize, Weak<Mutex<OverlayMap>>)],
    ) {
        match self.values.get(key) {
            None => MapValue::None.hash(sub_envs, hasher),
            Some(v) => v.hash(sub_envs, hasher),
        }
    }

    fn hash(&self, keys: &[String], hasher: &mut blake3::Hasher) {
        for key in keys {
            self.hash_key_with_envs(key, hasher, &[]);
        }
    }
}

impl private::RawGet for OverlayMap {
    fn get_raw(&self, key: &str) -> MapValue {
        match self.environment.values.get(key) {
            None => match &self.parent {
                OverlayParent::None => MapValue::None,
                OverlayParent::Current(e) | OverlayParent::Parent(e) | OverlayParent::Leaf(e) => {
                    e.lock().unwrap().get_raw(key)
                }
            },
            Some(v) => v.clone(),
        }
    }
}

impl private::Get for OverlayMap {
    fn get(&mut self, key: &str) -> MapValue {
        use private::RawGet;
        self.environment.used_keys.insert(key.to_string());
        self.get_raw(key)
    }
}

impl Lookup for OverlayMap {
    fn get_string_vec(&mut self, key: &str) -> Vec<String> {
        use private::Get;
        self.get(key).as_string_vec(&self.sub_envs)
    }
}

impl RawLookup for OverlayMap {
    fn get_string_vec_raw(&self, key: &str) -> Vec<String> {
        use private::RawGet;
        self.get_raw(key).as_string_vec(&self.sub_envs)
    }
}

impl Hash for OverlayMap {
    fn hash_key_with_envs(
        &self,
        key: &str,
        hasher: &mut blake3::Hasher,
        sub_envs: &[(usize, Weak<Mutex<OverlayMap>>)],
    ) {
        hasher.update(key.as_bytes());
        match self.environment.values.get(key) {
            None => match &self.parent {
                OverlayParent::None => MapValue::None.hash(sub_envs, hasher),
                OverlayParent::Current(e) | OverlayParent::Parent(e) | OverlayParent::Leaf(e) => {
                    e.lock().unwrap().hash_key_with_envs(key, hasher, sub_envs)
                }
            },
            Some(v) => v.hash(sub_envs, hasher),
        }
    }

    fn hash(&self, keys: &[String], hasher: &mut blake3::Hasher) {
        for key in keys {
            self.hash_key_with_envs(key, hasher, &self.sub_envs);
        }
        hasher
            .update("sub_envs".as_bytes())
            .update(&self.sub_envs.len().to_ne_bytes());
    }
}
