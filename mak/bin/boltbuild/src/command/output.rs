use crate::command::{CommandOutput, SerializedHash};
use crate::context::TOOLS_DIR;
use crate::environment::{FlatMap, Hash, OverlayMap};
use crate::node::Node;
use blake3::Hasher;
use std::iter::zip;
use std::sync::{Arc, Mutex};

impl CommandOutput {
    pub(crate) fn hash(
        &self,
        options: Option<&FlatMap>,
        envs: &[Arc<Mutex<OverlayMap>>],
        tools: &Vec<Node>,
    ) -> std::io::Result<(
        SerializedHash,
        SerializedHash,
        SerializedHash,
        SerializedHash,
    )> {
        let hash1 = {
            let mut hasher = Hasher::new();
            for file in &self.stored_hash.file_dependencies {
                if file.is_file() {
                    hasher.update(file.as_os_str().as_encoded_bytes());
                    hasher.update_reader(std::fs::File::open(file)?)?;
                } else {
                    hasher.update("!file_not_found!".as_bytes());
                    hasher.update(file.as_os_str().as_encoded_bytes());
                }
            }
            SerializedHash(hasher.finalize())
        };

        let hash2 = {
            let mut hasher = Hasher::new();
            for file in tools {
                hasher.update(file.path().as_os_str().as_encoded_bytes());
                if let Ok(file) = std::fs::File::open(file.path()) {
                    hasher.update_reader(file)?;
                } else if let Some(file) = TOOLS_DIR.get_file(file.path()) {
                    hasher.update(file.contents());
                } else {
                    hasher.update("!file_not_found!".as_bytes());
                }
            }
            SerializedHash(hasher.finalize())
        };

        let hash3 = {
            let mut hasher = Hasher::new();
            if let Some(env) = options {
                env.hash(&self.stored_hash.option_dependencies, &mut hasher);
            }
            SerializedHash(hasher.finalize())
        };

        let hash4 = {
            let mut hasher = Hasher::new();
            for (vars, env_arc) in zip(self.stored_hash.variable_dependencies.iter(), envs.iter()) {
                let env = env_arc.lock().unwrap();
                env.hash(vars, &mut hasher);
            }
            SerializedHash(hasher.finalize())
        };

        Ok((hash1, hash2, hash3, hash4))
    }
}
