use super::Generator;

impl Generator {
    pub(crate) fn new(name: String, group: String, features: Vec<String>) -> Self {
        Self { name, group, features, posted: false }
    }
}