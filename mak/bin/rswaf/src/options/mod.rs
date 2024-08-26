mod lua;
mod options;
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

