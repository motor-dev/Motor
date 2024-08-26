use crate::command::CommandSpec;

impl CommandSpec {
    pub(super) fn create_init() -> Self {
        Self {
            name: "init".to_string(),
            function: "init".to_string(),
            envs: vec![0],
        }
    }
}