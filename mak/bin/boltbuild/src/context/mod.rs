mod operations;
mod lua_binding;
mod subprocess;
mod task;

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::path::PathBuf;
use crate::command::{CommandSpec, CommandOutput};
use crate::environment::ReadWriteEnvironment;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use crate::task::Task;

pub(crate) struct Context {
    spec: CommandSpec,
    pub(crate) output: CommandOutput,
    environment: Arc<Mutex<ReadWriteEnvironment>>,
    pub(crate) tasks: Vec<Task>,
    pub(crate) products: HashMap<PathBuf, usize>,
    pub(crate) signatures: Vec<blake3::Hasher>,
    task_dependencies: Vec<(usize, usize)>,
    path: Node,
    src_dir: Node,
    bld_dir: Node,
    options: Options,
    logger: Logger,
    command_path: Vec<String>,
    commands: HashMap<String, Vec<String>>,
    sorted_features: Vec<String>,
    partial_order: Vec<(String, String)>,
    in_post: usize,
}