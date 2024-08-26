mod lua;
mod task;

use crate::node::Node;

pub(crate) struct Task {
    name: String,
    inputs: Vec<Node>,
    output: Vec<Node>,
}

