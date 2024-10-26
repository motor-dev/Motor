use super::Output;
use crate::task::Task;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub(super) struct DependencyCommandDriverConfiguration {
    command: String,
}

impl DependencyCommandDriverConfiguration {
    pub(super) fn new(command: String) -> Self {
        Self {
            command
        }
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let (command, log, exit_code) = task.run_command(self.command.as_str());
        Output {
            exit_code,
            command,
            log,
            dependencies: Vec::new(),
        }
    }
}
