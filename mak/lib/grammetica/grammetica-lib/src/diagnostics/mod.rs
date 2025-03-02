pub enum Location {
    LexRule(usize, Option<(usize, usize)>),
    ParseRule(usize, Option<usize>),
}

pub struct Error {
    pub location: Location,
    pub message: String,
    pub next: Option<Box<Error>>,
}

pub type Result<T> = std::result::Result<T, Error>;

impl Error {
    pub fn new_lex_error(
        lex_index: usize,
        location: Option<(usize, usize)>,
        message: String,
        next: Option<Self>,
    ) -> Self {
        Self {
            location: Location::LexRule(lex_index, location),
            message,
            next: next.map(Box::new),
        }
    }

    pub fn new_parse_error(
        parse_index: usize,
        item_index: Option<usize>,
        message: String,
        next: Option<Self>,
    ) -> Self {
        Self {
            location: Location::ParseRule(parse_index, item_index),
            message,
            next: next.map(Box::new),
        }
    }
}
