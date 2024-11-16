mod operations;
mod lua_binding;
mod subprocess;
mod task;
mod log;
mod driver;
mod generator;
mod command;
mod environment;
mod node;
mod feature;

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::path::PathBuf;
use include_dir::{Dir, include_dir};
use crate::command::{CommandSpec, CommandOutput};
use crate::environment::ReadWriteEnvironment;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use crate::task::Task;

pub(crate) static TOOLS_DIR: Dir = include_dir!("$CARGO_MANIFEST_DIR/tools");

pub(crate) struct Context {
    spec: CommandSpec,
    pub(crate) output: CommandOutput,
    environment: Arc<Mutex<ReadWriteEnvironment>>,
    pub(crate) tasks: Vec<Task>,
    pub(crate) products: HashMap<PathBuf, usize>,
    pub(crate) signatures: Vec<blake3::Hasher>,
    task_dependencies: Vec<(usize, usize, String)>,
    path: Node,
    src_dir: Node,
    bld_dir: Node,
    options: Options,
    logger: Logger,
    command_path: Vec<String>,
    commands: HashMap<String, Vec<String>>,
    sorted_features: Vec<String>,
    partial_order: Vec<(String, String)>,
    pub(crate) driver_order: Vec<(String, String)>,
    pub(crate) driver_tasks: HashMap<String, Vec<usize>>,
    in_post: usize,
}