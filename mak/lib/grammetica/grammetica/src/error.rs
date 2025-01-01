use proc_macro2::Span;
use std::result::Result as StdResult;

pub(crate) struct Error {
    pub(crate) message: String,
    pub(crate) location: Span,
    pub(crate) note: Option<Box<Error>>,
}

impl Error {
    pub(crate) fn new(location: Span, message: String) -> Self {
        Self {
            message,
            location,
            note: None
        }
    }
}

pub(crate) type Result<T> = StdResult<T, Error>;
