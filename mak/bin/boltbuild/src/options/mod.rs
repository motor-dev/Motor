mod lua_binding;
mod command_line;


use crate::environment::{Environment};
use std::sync::{Arc, Mutex};

#[derive(Clone)]
pub(crate) enum Options {
    CommandLineParser(Arc<Mutex<CommandLineParser>>),
    Environment(Environment),
}

pub(crate) struct CommandLineParser {
    options: Vec<command_line::Argument>,
}


impl Options {
    pub(crate) fn from_parser(context: Arc<Mutex<CommandLineParser>>) -> Self {
        Options::CommandLineParser(context)
    }
    pub(crate) fn from_env(env: Environment) -> Self {
        Options::Environment(env)
    }
}
