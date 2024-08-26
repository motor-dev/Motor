mod context;
mod lua;
mod subprocess;

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use crate::command::{CommandSpec, CommandOutput};
use crate::environment::ReadWriteEnvironment;
use crate::log::Logger;
use crate::node::Node;
use crate::options::Options;

pub(crate) struct Context {
    spec: CommandSpec,
    pub(crate) output: CommandOutput,
    environment: Arc<Mutex<ReadWriteEnvironment>>,
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