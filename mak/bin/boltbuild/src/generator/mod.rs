use crate::context::INVALID_CHARS;
use crate::environment::OverlayMap;
use crate::node::Node;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

mod lua_binding;

pub(crate) struct Generator {
    pub(crate) name: String,
    pub(crate) path: Node,
    pub(crate) bld_dir: Node,
    pub(crate) group: String,
    pub(crate) env: Arc<Mutex<OverlayMap>>,
    pub(crate) features: Vec<String>,
    pub(crate) posted: bool,
}

impl Generator {
    pub(crate) fn new(
        name: String,
        path: &Node,
        bld_dir: &Node,
        env: Arc<Mutex<OverlayMap>>,
        group: String,
        features: Vec<String>,
    ) -> Self {
        let mut bld_dir = bld_dir.make_node(&PathBuf::from(
            INVALID_CHARS.replace_all(group.as_str(), "_").as_ref(),
        ));
        for p in name.split('/') {
            bld_dir = bld_dir.make_node(&PathBuf::from(INVALID_CHARS.replace_all(p, "_").as_ref()));
        }

        Self {
            name,
            path: path.clone(),
            bld_dir,
            group,
            env,
            features,
            posted: false,
        }
    }
}
