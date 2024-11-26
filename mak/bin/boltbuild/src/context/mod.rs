mod command;
mod debug;
mod driver;
mod environment;
mod feature;
mod generator;
mod log;
mod lua_binding;
mod node;
mod operations;
mod subprocess;
mod task;

use crate::command::{CommandOutput, CommandSpec};
use crate::environment::ReadWriteEnvironment;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;
use crate::task::Task;
use include_dir::{include_dir, Dir};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

pub(crate) static TOOLS_DIR: Dir = include_dir!("$CARGO_MANIFEST_DIR/tools");
pub(crate) static TOOLS_PATH: &'static str = env!("CARGO_MANIFEST_DIR");

pub(crate) struct Context {
    spec: CommandSpec,
    pub(crate) output: CommandOutput,
    environment: Arc<Mutex<ReadWriteEnvironment>>,
    pub(crate) tasks: Vec<Task>,
    pub(crate) products: HashMap<PathBuf, usize>,
    pub(crate) signatures: Vec<blake3::Hasher>,
    task_dependencies: Vec<Vec<(usize, String)>>,
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
