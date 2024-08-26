mod generator;
mod lua;

pub(crate) struct Generator {
    pub(crate) name: String,
    pub(crate) group: String,
    pub(crate) features: Vec<String>,
    pub(crate) posted: bool,
}