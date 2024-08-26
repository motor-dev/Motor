use std::iter::zip;
use std::sync::{Arc, Mutex};
use blake3::Hasher;
use crate::command::{CommandOutput, SerializedHash};
use crate::environment::{Environment, ReadWriteEnvironment};
use crate::node::Node;

impl CommandOutput {
    pub(crate) fn hash(
        &self,
        options: Option<&Environment>,
        envs: &Vec<Arc<Mutex<ReadWriteEnvironment>>>,
        tools: &Vec<Node>,
    ) -> std::io::Result<(SerializedHash, SerializedHash, SerializedHash, SerializedHash)> {
        let hash1 = {
            let mut hasher = Hasher::new();
            for file in &self.stored_hash.file_dependencies {
                hasher.update(file.as_os_str().as_encoded_bytes());
                hasher.update_reader(std::fs::File::open(file)?)?;
            }
            SerializedHash(hasher.finalize())
        };

        let hash2 = {
            let mut hasher = Hasher::new();
            for file in tools {
                hasher.update(file.path().as_os_str().as_encoded_bytes());
                hasher.update_reader(std::fs::File::open(file.path())?)?;
            }
            SerializedHash(hasher.finalize())
        };

        let hash3 = {
            let mut hasher = Hasher::new();
            if let Some(env) = options {
                for env_var in &self.stored_hash.option_dependencies {
                    env.get_raw(env_var.as_str()).hash(&mut hasher);
                }
            }
            SerializedHash(hasher.finalize())
        };

        let hash4 = {
            let mut hasher = Hasher::new();
            for (vars, env_arc) in zip(self.stored_hash.variable_dependencies.iter(), envs.iter()) {
                let env = env_arc.lock().unwrap();
                for var in vars {
                    env.get_raw(var.as_str()).hash(&mut hasher);
                }
            }
            SerializedHash(hasher.finalize())
        };

        Ok((hash1, hash2, hash3, hash4))
    }
}