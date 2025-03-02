use crate::environment::{FlatMap, Lookup};
use crate::node::Node;
use std::sync::{Arc, Mutex};

mod command_line;
mod lua_binding;

#[derive(Clone)]
pub(crate) enum Options {
    CommandLineParser(Arc<Mutex<CommandLineParser>>),
    Environment(Arc<Mutex<FlatMap>>),
}

pub(crate) struct CommandLineParser {
    options: Vec<command_line::Argument>,
    map: FlatMap,
}

impl Options {
    pub(crate) fn from_parser(context: Arc<Mutex<CommandLineParser>>) -> Self {
        Options::CommandLineParser(context)
    }
    pub(crate) fn from_env(env: FlatMap) -> Self {
        Options::Environment(Arc::new(Mutex::new(env)))
    }

    pub(crate) fn get_string(&self, key: &str) -> String {
        match self {
            Options::CommandLineParser(parser) => parser.lock().unwrap().map.get_string(key),
            Options::Environment(env) => env.lock().unwrap().get_string(key),
        }
    }

    pub(crate) fn get_node_vec(&self, key: &str, current_dir: &Node) -> Vec<Node> {
        match self {
            Options::CommandLineParser(parser) => {
                parser.lock().unwrap().map.get_node_vec(key, current_dir)
            }
            Options::Environment(env) => env.lock().unwrap().get_node_vec(key, current_dir),
        }
    }
}
