use crate::environment::{Environment, EnvironmentValue};
use std::sync::{Arc, Mutex};

mod command_line;
mod lua_binding;

#[derive(Clone)]
pub(crate) enum Options {
    CommandLineParser(Arc<Mutex<CommandLineParser>>),
    Environment(Arc<Mutex<Environment>>),
}

pub(crate) struct CommandLineParser {
    options: Vec<command_line::Argument>,
}

impl Options {
    pub(crate) fn from_parser(context: Arc<Mutex<CommandLineParser>>) -> Self {
        Options::CommandLineParser(context)
    }
    pub(crate) fn from_env(env: Environment) -> Self {
        Options::Environment(Arc::new(Mutex::new(env)))
    }

    pub(crate) fn get_value(&mut self, name: &str) -> Option<EnvironmentValue> {
        match self {
            Options::CommandLineParser(parser) => parser.lock().unwrap().get_value(name),
            Options::Environment(env) => env.lock().unwrap().get(name),
        }
    }
}
