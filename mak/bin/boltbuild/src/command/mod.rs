use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use blake3::Hash;
use serde::{Deserialize, Serialize};
use crate::environment::{Environment, ReadWriteEnvironment};
use crate::node::Node;
use crate::task::Task;

mod run;
mod scheduler;
mod serialization;
mod output;
mod spec;

#[derive(Serialize)]
pub(crate) struct Command {
    pub(crate) spec: CommandSpec,
    pub(crate) output: Option<CommandOutput>,
    pub(crate) status: CommandStatus,
}

#[derive(Serialize, Deserialize)]
pub(crate) enum CommandStatus {
    ForwardDeclared,
    Defined,
    Cached,
    UpToDate,
}

#[derive(Clone, Serialize, Deserialize)]
pub(crate) struct CommandSpec {
    pub(crate) name: String,
    pub(crate) function: String,
    pub(crate) envs: Vec<usize>,
}

#[derive(Serialize, Deserialize)]
pub(crate) enum GroupStatus {
    Default,
    Enabled,
    Disabled,
    Conditional(String),
}

pub(crate) enum TaskSeq {
    None,
    List(Vec<Task>),
    Cached(PathBuf),
}

pub(crate) struct CommandOutput {
    pub(crate) environments: Vec<Arc<Mutex<ReadWriteEnvironment>>>,
    pub(crate) commands: Vec<Command>,
    pub(crate) options: Option<Environment>,
    pub(crate) tools: Vec<Node>,
    pub(crate) stored_hash: CommandHash,
    pub(crate) groups: Vec<(String, GroupStatus)>,
    pub(crate) tasks: TaskSeq,
}

#[derive(Serialize, Deserialize)]
pub(crate) struct CommandHash {
    pub(crate) file_dependencies: Vec<PathBuf>,
    pub(crate) option_dependencies: Vec<String>,
    pub(crate) variable_dependencies: Vec<Vec<String>>,
    pub(crate) glob_dependencies: Vec<(Node, String, SerializedHash)>,
    pub(crate) hash: Option<(SerializedHash, SerializedHash, SerializedHash, SerializedHash)>,
}

#[derive(PartialEq, Eq, Hash, Clone)]
pub(crate) struct SerializedHash(pub Hash);

impl Command {
    pub(crate) fn init() -> crate::error::Result<Self> {
        let init_command = Command {
            spec: CommandSpec::create_init(),
            output: None,
            status: CommandStatus::Defined,
        };
        Ok(init_command)
    }
}
