use super::Options;
use super::CommandLineParser;
use std::sync::{Arc, Mutex};
use crate::environment::Environment;

impl Options {
    pub(crate) fn from_parser(context: Arc<Mutex<CommandLineParser>>) -> Self {
        Options::CommandLineParser(context)
    }
    pub(crate) fn from_env(env: Environment) -> Self {
        Options::Environment(env)
    }
}
