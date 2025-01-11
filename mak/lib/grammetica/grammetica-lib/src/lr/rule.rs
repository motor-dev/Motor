pub(super) struct Rule {
    id: usize,
    production: usize,
    symbols: Vec<usize>,
}

impl Rule {
    pub(super) fn new(id: usize, production: usize, symbols: Vec<usize>) -> Self {
        Self {
            id,
            production,
            symbols,
        }
    }
}