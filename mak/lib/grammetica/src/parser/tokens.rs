use super::Result;
use crate::error::Error;
use proc_macro::token_stream::IntoIter;
use proc_macro::{Delimiter, Ident, Literal, Punct, Spacing, Span, TokenStream, TokenTree};

pub(super) fn from_dsl(grammar: TokenStream) -> Result<()> {
    let mut grammar = grammar.into_iter();
    while let Some(token) = grammar.next() {
        match token {
            TokenTree::Ident(identifier) => {
                parse_token_identifier(identifier, &mut grammar)?;
            }
            TokenTree::Literal(literal) => {
                parse_token_literal(literal, &mut grammar)?;
            }
            TokenTree::Group(group) if group.delimiter() == Delimiter::Bracket => loop {
                match grammar.next() {
                    Some(TokenTree::Ident(ident)) => {
                        break parse_token_identifier(ident, &mut grammar)?;
                    }
                    Some(TokenTree::Literal(literal)) => {
                        break parse_token_literal(literal, &mut grammar)?;
                    }
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Bracket => {
                        // add more tags
                        continue;
                    }
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Brace => {
                        break from_dsl(group.stream())?;
                    }
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
            },
            _ => {
                return Err(Error::new(
                    token.span(),
                    format!("Unexpected token {:?} in token section", token),
                ));
            }
        }
    }
    Ok(())
}

fn parse_token_identifier(identifier: Ident, rule: &mut IntoIter) -> Result<()> {
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == ':' => {
            parse_typed_token(identifier.span(), punct, rule)
        }
        Some(TokenTree::Punct(punct))
            if punct.as_char() == '=' && punct.spacing() == Spacing::Joint =>
        {
            parse_untyped_token(identifier.span(), rule)
        }
        Some(token) => Err(Error::new(
            token.span(),
            format!(
                "Unexpected token `{:?}` in token definition: expected `:` or `=>`",
                token
            ),
        )),
        None => Err(Error::new(
            identifier.span(),
            format!(
                "Unexpected end of input: expected `=>` after token `{}`.",
                identifier
            ),
        )),
    }
}

fn parse_token_literal(literal: Literal, rule: &mut IntoIter) -> Result<()> {
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct == ';' => Ok(()),
        Some(token) => Err(Error::new(
            token.span(),
            format!(
                "Unexpected token `{:?}` in literal token definition: expected `;`.",
                token
            ),
        )),
        None => Err(Error::new(
            literal.span(),
            format!(
                "Unexpected end of input: expected `;` after literal token `{}`.",
                literal
            ),
        )),
    }
}

fn parse_typed_token(location: Span, punct: Punct, rule: &mut IntoIter) -> Result<()> {
    let t = rule.next();
    if t.is_none() {
        return Err(Error::new(
            punct.span(),
            "Unexpected end of input after `:`: expected a type".to_string(),
        ));
    }
    let result_type = t.unwrap();

    match rule.next() {
        None => Err(Error::new(
            result_type.span(),
            "Unexpected end of input after type: expected `;` or `=>`".to_string(),
        )),
        Some(TokenTree::Punct(p)) if p.as_char() == ';' => Ok(()),
        Some(TokenTree::Punct(p)) if p.as_char() == '=' && p.spacing() == Spacing::Joint => {
            parse_untyped_token(location, rule)
        }
        Some(other) => Err(Error::new(
            other.span(),
            "Unexpected token after type: expected `;` or `=>`".to_string(),
        )),
    }
}

fn parse_untyped_token(location: Span, rule: &mut IntoIter) -> Result<()> {
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == '>' => parse_token_value(punct, rule),
        Some(token) => Err(Error::new(
            token.span(),
            format!(
                "Unexpected token `{:?}` in token definition: expected `=>`",
                token
            ),
        )),
        None => Err(Error::new(
            location,
            "Unexpected end of input: expected `=>`.".to_string(),
        )),
    }
}

fn parse_token_value(punct: Punct, rule: &mut IntoIter) -> Result<()> {
    match rule.next() {
        Some(TokenTree::Literal(literal)) => parse_token_action(literal, rule),
        Some(other) => Err(Error::new(
            other.span(),
            format!(
                "Unexpected token `{:?}` in token definition: expected a string literal",
                other
            ),
        )),
        None => Err(Error::new(
            punct.span(),
            "Unexpected end of input: expected `{{`.".to_string(),
        )),
    }
}

fn parse_token_action(literal: Literal, rule: &mut IntoIter) -> Result<()> {
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == ';' => Ok(()),
        Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Brace => Ok(()),
        Some(other) => Err(Error::new(
            other.span(),
            format!(
                "Unexpected token `{:?}` in token definition: expected `;`",
                other
            ),
        )),
        None => Err(Error::new(
            literal.span(),
            "Unexpected end of input: expected `;`.".to_string(),
        )),
    }
}
