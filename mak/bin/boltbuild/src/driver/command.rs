use super::Output;
use crate::task::Task;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct CommandDriverConfiguration {
    command: String,
}

impl CommandDriverConfiguration {
    pub(super) fn new(command: String) -> Self {
        Self {
            command
        }
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let (exit_code, log, command) = task.run_command(self.command.as_str(), Vec::new());
        Output {
            exit_code,
            command,
            log,
            file_dependencies: Vec::new(),
            extra_output: Vec::new(),
        }
    }
}
