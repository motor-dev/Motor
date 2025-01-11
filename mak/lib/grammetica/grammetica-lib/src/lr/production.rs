use super::rule::Rule;

pub(super) struct Production {
    product: usize,
    rules: Vec<Rule>,
}

impl Production {
    pub(super) fn new(product: usize) -> Self {
        Self {
            product,
            rules: Vec::new(),
        }
    }

    pub(super) fn add_rule(&mut self, id: usize, product: usize, rule: Vec<usize>) {
        self.rules.push(Rule::new(id, product, rule));
    }
}
