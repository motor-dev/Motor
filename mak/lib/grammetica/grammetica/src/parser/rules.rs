use super::{parse_extended_identifier, Error, Result};
use proc_macro2::token_stream::IntoIter;
use proc_macro2::{Delimiter, Ident, Spacing, Span, TokenStream, TokenTree};
use quote::TokenStreamExt;

pub(super) enum Precedence {
    Left(u32),
    Right(u32),
    None,
}

pub(super) enum Split {
    Yes,
    No,
}

pub(super) struct Symbol {
    pub(super) value: String,
    pub(super) location: Span,
    pub(super) precedence: Precedence,
    pub(super) split: Split,
}

pub(super) struct Rule {
    pub(super) name: String,
    pub(super) location: Span,
    pub(super) ty: Option<TokenStream>,
    pub(super) production: Option<Vec<Symbol>>,
    pub(super) action: Option<TokenStream>,
    pub(super) conditions: Vec<(bool, String)>,
}

pub(super) fn from_dsl(grammar: TokenStream) -> Result<Vec<Rule>> {
    let mut grammar = grammar.into_iter();
    let mut result = Vec::new();
    while let Some(token) = grammar.next() {
        match token {
            TokenTree::Ident(ident) => {
                result.push(parse_rule(ident, &mut grammar)?);
            }
            TokenTree::Group(group) if group.delimiter() == Delimiter::Bracket => loop {
                match grammar.next() {
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Bracket => {
                        continue;
                    }
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Brace => {
                        result.extend(from_dsl(group.stream())?);
                        break;
                    }
                    Some(value) => match value {
                        TokenTree::Ident(ident) => {
                            result.push(parse_rule(ident, &mut grammar)?);
                        }
                        _ => {
                            return Err(Error::new(
                                value.span(),
                                "Unexpected token after tag".to_string(),
                            ));
                        }
                    },
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
                    format!("Unexpected token {:?} in rule section", token),
                ));
            }
        }
    }
    Ok(result)
}

fn parse_rule(identifier: Ident, rule: &mut IntoIter) -> Result<Rule> {
    //let mut result_type = None;
    let (name, span) = parse_extended_identifier(&identifier, rule);
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == ':' => {
            let (ty, symbols, action) = parse_typed_rule(span, rule)?;
            Ok(Rule {
                name,
                location: span,
                ty: Some(ty),
                production: symbols,
                action,
                conditions: Vec::new(),
            })
        }
        Some(TokenTree::Punct(punct))
            if punct.as_char() == '=' && punct.spacing() == Spacing::Joint =>
        {
            let (symbols, action) = parse_untyped_rule(span, rule)?;
            Ok(Rule {
                name,
                location: span,
                ty: None,
                production: Some(symbols),
                action,
                conditions: Vec::new(),
            })
        }
        Some(token) => Err(Error::new(
            token.span(),
            format!(
                "Unexpected token `{:?}` in rule section: expected `:` or `=>`",
                token
            ),
        )),
        None => Err(Error::new(
            identifier.span(),
            format!(
                "Unexpected end of input: expected a value for section `{}`.",
                identifier
            ),
        )),
    }
}

fn parse_typed_rule(
    location: Span,
    rule: &mut IntoIter,
) -> Result<(TokenStream, Option<Vec<Symbol>>, Option<TokenStream>)> {
    let t = rule.next();
    if t.is_none() {
        return Err(Error::new(
            location,
            "Unexpected end of input after `:`: expected a type".to_string(),
        ));
    }
    let t = t.unwrap();
    let mut location = t.span();
    let mut result_type = TokenStream::new();
    result_type.append(t);

    loop {
        match rule.next() {
            None => {
                break Err(Error::new(
                    location,
                    "Unexpected end of input after type: expected a rule".to_string(),
                ))
            }
            Some(TokenTree::Punct(p)) if p.as_char() == ';' => break Ok((result_type, None, None)),
            Some(TokenTree::Punct(p)) if p.as_char() == '=' && p.spacing() == Spacing::Joint => {
                let (symbols, action) = parse_untyped_rule(p.span(), rule)?;
                break Ok((result_type, Some(symbols), action));
            }
            Some(other) => {
                location = other.span();
                result_type.append(other);
            }
        }
    }
}

fn parse_untyped_rule(
    location: Span,
    rule: &mut IntoIter,
) -> Result<(Vec<Symbol>, Option<TokenStream>)> {
    match rule.next() {
        None => Err(Error::new(
            location,
            "Unexpected end of input after `=`: expected `=>`".to_string(),
        )),
        Some(TokenTree::Punct(p)) if p.as_char() == '>' => parse_expansion(p.span(), rule),
        Some(other) => Err(Error::new(
            other.span(),
            "Unexpected token after `=`: expected `=>`".to_string(),
        )),
    }
}

fn parse_expansion(
    location: Span,
    rule: &mut IntoIter,
) -> Result<(Vec<Symbol>, Option<TokenStream>)> {
    let mut symbols = Vec::new();
    while let Some(token) = rule.next() {
        match &token {
            TokenTree::Ident(ident) => {
                let (name, span) = parse_extended_identifier(ident, rule);
                symbols.push(Symbol {
                    value: name,
                    location: span,
                    precedence: Precedence::None,
                    split: Split::No,
                });
            }
            TokenTree::Literal(literal) => {
                let value = litrs::StringLit::try_from(literal).map_err(|error| {
                    Error::new(literal.span(), format!("Invalid token name: {}", error))
                })?;
                symbols.push(Symbol {
                    value: value.value().to_string(),
                    location: literal.span(),
                    precedence: Precedence::None,
                    split: Split::No,
                });
            }
            TokenTree::Punct(punct) if punct.as_char() == ';' => {
                return Ok((symbols, None));
            }
            TokenTree::Group(group) if group.delimiter() == Delimiter::Bracket => loop {
                match rule.next() {
                    Some(TokenTree::Ident(ident)) => {
                        let (name, span) = parse_extended_identifier(&ident, rule);
                        symbols.push(Symbol {
                            value: name,
                            location: span,
                            precedence: Precedence::None,
                            split: Split::No,
                        });
                        break;
                    }
                    Some(TokenTree::Literal(literal)) => {
                        let value = litrs::StringLit::try_from(&literal).map_err(|error| {
                            Error::new(literal.span(), format!("Invalid token name: {}", error))
                        })?;
                        symbols.push(Symbol {
                            value: value.value().to_string(),
                            location: literal.span(),
                            precedence: Precedence::None,
                            split: Split::No,
                        });
                        break;
                    }
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Bracket => {
                        continue;
                    }
                    Some(_) => {
                        return Err(Error::new(
                            token.span(),
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
            TokenTree::Group(group) if group.delimiter() == Delimiter::Brace => {
                return Ok((symbols, Some(group.stream())));
            }
            _ => {
                return Err(Error::new(
                    token.span(),
                    format!("Unexpected token `{:?}` in rule section", token),
                ));
            }
        }
    }
    Err(Error::new(
        location,
        "Unexpected end of input after rule expansion".to_string(),
    ))
}
