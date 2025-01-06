use proc_macro2::Span;

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
            note: None,
        }
    }
    pub(crate) fn new_with(location: Span, message: String, next: Error) -> Self {
        Self {
            message,
            location,
            note: Some(Box::new(next)),
        }
    }
}

pub(crate) type Result<T> = std::result::Result<T, Error>;
