use super::Result;
use crate::error::Error;
use proc_macro2::{Delimiter, Ident, TokenStream, TokenTree};
use proc_macro2::token_stream::IntoIter;

pub(super) fn from_dsl(grammar: TokenStream) -> Result<()> {
    let mut grammar = grammar.into_iter();
    while let Some(token) = grammar.next() {
        match token {
            TokenTree::Ident(identifier) => {
                parse_variant(identifier, &mut grammar)?;
            }
            _ => {
                return Err(Error::new(
                    token.span(),
                    format!("Unexpected token {:?} in variant section", token),
                ));
            }
        }
    }
    Ok(())
}

fn parse_variant(identifier: Ident, grammar: &mut IntoIter) -> Result<()> {
    match grammar.next() {
        Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Bracket => {
            match grammar.next() {
                Some(TokenTree::Punct(punct)) if punct.as_char() == ';' => Ok(()),
                Some(other) => Err(Error::new(
                    other.span(),
                    "Unexpected token after variant value".to_string(),
                )),
                None => Err(Error::new(
                    identifier.span(),
                    "Unexpected end of input after variant identifier".to_string(),
                )),
            }
        }
        Some(other) => Err(Error::new(
            other.span(),
            "Unexpected token after variant identifier".to_string(),
        )),
        None => Err(Error::new(
            identifier.span(),
            "Unexpected end of input after variant identifier".to_string(),
        )),
    }
}
