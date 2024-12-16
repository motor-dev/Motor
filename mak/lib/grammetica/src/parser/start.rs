use super::Result;
use crate::error::Error;
use proc_macro::{Delimiter, TokenStream, TokenTree};

pub(super) fn from_dsl(grammar: TokenStream) -> Result<()> {
    let mut tokens = grammar.into_iter();
    while let Some(token) = tokens.next() {
        match token {
            TokenTree::Ident(ident) => match tokens.next() {
                Some(TokenTree::Punct(punct)) if punct.as_char() == ';' => {
                    continue;
                }
                Some(other) => {
                    return Err(Error::new(
                        other.span(),
                        "Unexpected token after start directive".to_string(),
                    ));
                }
                None => {
                    return Err(Error::new(
                        ident.span(),
                        "Unexpected end of input after start directive".to_string(),
                    ));
                }
            },
            TokenTree::Group(group) if group.delimiter() == Delimiter::Bracket => {
                match tokens.next() {
                    Some(TokenTree::Ident(ident)) => match tokens.next() {
                        Some(TokenTree::Punct(punct)) if punct.as_char() == ';' => {
                            continue;
                        }
                        Some(other) => {
                            return Err(Error::new(
                                other.span(),
                                "Unexpected token after start directive".to_string(),
                            ));
                        }
                        None => {
                            return Err(Error::new(
                                ident.span(),
                                "Unexpected end of input after start directive".to_string(),
                            ));
                        }
                    },
                    Some(other) => {
                        return Err(Error::new(
                            other.span(),
                            "Unexpected token after variant tag".to_string(),
                        ));
                    }
                    None => {
                        return Err(Error::new(
                            group.span(),
                            "Unexpected end of input after variant tag".to_string(),
                        ));
                    }
                }
            }
            _ => {
                return Err(Error::new(
                    token.span(),
                    format!("Unexpected token `{:?}` in start section", token),
                ));
            }
        }
    }
    Ok(())
}
