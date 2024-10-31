pub struct Location(pub String, pub u32);

pub struct MakeError {
    pub location: Option<Location>,
    pub message: String,
}

pub type Result<T> = std::result::Result<T, MakeError>;

impl From<std::io::Error> for MakeError {
    fn from(err: std::io::Error) -> Self {
        Self {
            location: None,
            message: err.to_string(),
        }
    }
}

impl From<mlua::Error> for MakeError {
    fn from(err: mlua::Error) -> Self {
        Self {
            location: None,
            message: err.to_string(),
        }
    }
}

impl From<&str> for MakeError {
    fn from(err: &str) -> Self {
        Self {
            location: None,
            message: err.to_string(),
        }
    }
}

impl From<String> for MakeError {
    fn from(err: String) -> Self {
        Self {
            location: None,
            message: err,
        }
    }
}

impl From<serde_json::Error> for MakeError {
    fn from(error: serde_json::Error) -> Self {
        Self {
            location: None,
            message: error.to_string(),
        }
    }
}

impl From<bincode::error::DecodeError> for MakeError {
    fn from(error: bincode::error::DecodeError) -> Self {
        Self {
            location: None,
            message: error.to_string(),
        }
    }
}

impl From<bincode::error::EncodeError> for MakeError {
    fn from(error: bincode::error::EncodeError) -> Self {
        Self {
            location: None,
            message: error.to_string(),
        }
    }
}
