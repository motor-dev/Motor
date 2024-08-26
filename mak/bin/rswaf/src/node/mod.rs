mod lua;
mod node;

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Clone, Serialize, Deserialize, PartialEq)]
pub(crate) struct Node {
    path: PathBuf,
}
