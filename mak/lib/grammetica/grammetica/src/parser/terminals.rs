use super::Result;
use super::{parse_extended_identifier, Error};
use proc_macro2::token_stream::IntoIter;
use proc_macro2::{Delimiter, Ident, Literal, Punct, Spacing, Span, TokenStream, TokenTree};

pub(super) struct Terminal {
    pub(super) name: String,
    pub(super) location: Span,
    pub(super) value_location: Span,
    pub(super) ty: Option<TokenTree>,
    pub(super) value: String,
    pub(super) action: Option<TokenStream>,
    pub(super) conditions: Vec<(bool, String)>,
}

pub(super) fn from_dsl(grammar: TokenStream) -> Result<Vec<Terminal>> {
    let mut grammar = grammar.into_iter();
    let mut result = Vec::new();
    while let Some(token) = grammar.next() {
        match token {
            TokenTree::Ident(identifier) => {
                result.push(parse_token_identifier(identifier, &mut grammar)?);
            }
            TokenTree::Literal(literal) => {
                result.push(parse_token_literal(literal, &mut grammar)?);
            }
            TokenTree::Group(group) if group.delimiter() == Delimiter::Bracket => loop {
                match grammar.next() {
                    Some(TokenTree::Ident(ident)) => {
                        break result.push(parse_token_identifier(ident, &mut grammar)?);
                    }
                    Some(TokenTree::Literal(literal)) => {
                        break result.push(parse_token_literal(literal, &mut grammar)?);
                    }
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Bracket => {
                        // add more tags
                        continue;
                    }
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Brace => {
                        break result.extend(from_dsl(group.stream())?);
                    }
                    Some(other) => {
                        return Err(Error::new(
                            other.span(),
                            "Unexpected token after tag".to_string(),
                        ));
                    }
                    None => {
                        return Err(Error::new(
                            group.span(),
                            "Unexpected end of input after tag".to_string(),
                        ));
                    }
                }
            },
            _ => {
                return Err(Error::new(
                    token.span(),
                    format!("Unexpected token {:?} in `literals` section", token),
                ));
            }
        }
    }
    Ok(result)
}

fn parse_token_literal(literal: Literal, rule: &mut IntoIter) -> Result<Terminal> {
    let value = litrs::StringLit::try_from(&literal).map_err(|error| {
        Error::new(literal.span(), format!("Invalid literal name: `{}`", error))
    })?;
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == ';' => Ok(Terminal {
            name: value.value().to_string(),
            location: literal.span(),
            value_location: literal.span(),
            ty: None,
            value: value.value().to_string(),
            action: None,
            conditions: Vec::new(),
        }),
        Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Brace => Ok(Terminal {
            name: value.value().to_string(),
            location: literal.span(),
            value_location: literal.span(),
            ty: None,
            value: value.value().to_string(),
            action: Some(group.stream()),
            conditions: Vec::new(),
        }),
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

fn parse_token_identifier(identifier: Ident, rule: &mut IntoIter) -> Result<Terminal> {
    let (name, location) = parse_extended_identifier(&identifier, rule);

    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == ':' => {
            let (ty, value, value_location, action) = parse_typed_token(punct, rule)?;
            Ok(Terminal {
                name: name.clone(),
                location: location.clone(),
                value_location: value_location.unwrap_or(location),
                ty: Some(ty),
                value: value.unwrap_or(name),
                action,
                conditions: Vec::new(),
            })
        }
        Some(TokenTree::Punct(punct))
            if punct.as_char() == '=' && punct.spacing() == Spacing::Joint =>
        {
            let (value, value_location, action) = parse_untyped_token(identifier.span(), rule)?;
            Ok(Terminal {
                name,
                location,
                value_location,
                ty: None,
                value,
                action,
                conditions: Vec::new(),
            })
        }
        Some(token) => Err(Error::new(
            token.span(),
            format!(
                "Unexpected token `{:?}` in token definition: expected `:` or `=>`",
                token
            ),
        )),
        None => Err(Error::new(
            location,
            format!(
                "Unexpected end of input: expected `=>` after token `{}`.",
                identifier
            ),
        )),
    }
}

fn parse_typed_token(
    punct: Punct,
    rule: &mut IntoIter,
) -> Result<(TokenTree, Option<String>, Option<Span>, Option<TokenStream>)> {
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
        Some(TokenTree::Punct(p)) if p.as_char() == ';' => Ok((result_type, None, None, None)),
        Some(TokenTree::Punct(p)) if p.as_char() == '=' && p.spacing() == Spacing::Joint => {
            print!("punct: {:?}", p);
            let (value, location, action) = parse_untyped_token(p.span(), rule)?;
            Ok((result_type, Some(value), Some(location), action))
        }
        Some(other) => Err(Error::new(
            other.span(),
            "Unexpected token after type: expected `;` or `=>`".to_string(),
        )),
    }
}

fn parse_untyped_token(
    location: Span,
    rule: &mut IntoIter,
) -> Result<(String, Span, Option<TokenStream>)> {
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

fn parse_token_value(
    punct: Punct,
    rule: &mut IntoIter,
) -> Result<(String, Span, Option<TokenStream>)> {
    match rule.next() {
        Some(TokenTree::Literal(literal)) => {
            let regexp = litrs::StringLit::try_from(&literal).map_err(|error| {
                Error::new(literal.span(), format!("Invalid token rule: {}", error))
            })?;
            let regexp = regexp.value();

            Ok((
                regexp.to_string(),
                literal.span(),
                parse_token_action(literal.span(), rule)?,
            ))
        }
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

fn parse_token_action(span: Span, rule: &mut IntoIter) -> Result<Option<TokenStream>> {
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == ';' => Ok(None),
        Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Brace => {
            Ok(Some(group.stream()))
        }
        Some(other) => Err(Error::new(
            other.span(),
            format!(
                "Unexpected token `{:?}` in token definition: expected `;`",
                other
            ),
        )),
        None => Err(Error::new(
            span,
            "Unexpected end of input: expected `;`.".to_string(),
        )),
    }
}
