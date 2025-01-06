use super::error::{Error, Result};
use proc_macro2::token_stream::IntoIter;
use proc_macro2::{Delimiter, Ident, Punct, Spacing, Span, TokenStream, TokenTree};

mod parse;
mod rules;
mod start;
mod terminals;
mod variants;

use rules::Rule;
use terminals::Terminal;

pub(super) struct Grammar {
    parameters: TokenStream,
    terminals: Vec<Terminal>,
    rules: Vec<Rule>,
}

fn invalid_token(token: TokenTree, expected: &str) -> Error {
    match token {
        TokenTree::Ident(ident) => Error::new(
            ident.span(),
            format!("Unexpected identifier `{}`. {}.", ident, expected),
        ),
        TokenTree::Punct(punct) => Error::new(
            punct.span(),
            format!("Unexpected token `{}`. {}.", punct, expected),
        ),
        TokenTree::Literal(literal) => Error::new(
            literal.span(),
            format!("Unexpected literal `{}`. {}.", literal, expected),
        ),
        TokenTree::Group(group) => Error::new(
            group.span_open(),
            format!(
                "Unexpected {} block. {}.",
                match group.delimiter() {
                    Delimiter::Brace => "{}",
                    Delimiter::Parenthesis => "()",
                    Delimiter::Bracket => "[]",
                    Delimiter::None => "macro",
                },
                expected
            ),
        ),
    }
}

fn duplicate_section(token: &Ident, section: &str) -> Error {
    Error::new(
        token.span(),
        format!("Section `{}`already defined.", section),
    )
}

fn missing_value(token: &Ident, section: &str) -> Error {
    Error::new(
        token.span(),
        format!(
            "Unexpected end of input: expected a value for section `{}`.",
            section
        ),
    )
}

fn consume_parameter(iterator: &mut IntoIter, append_semi: bool) -> Option<TokenStream> {
    let value = iterator.next()?;
    if let TokenTree::Group(group) = &value {
        if group.delimiter() == Delimiter::Brace {
            return Some(group.stream());
        }
    }

    let mut result = TokenStream::new();
    result.extend([value]);
    for value in iterator.by_ref() {
        if let TokenTree::Punct(punct) = &value {
            if punct.as_char() == ';' {
                if append_semi {
                    result.extend([value]);
                }
                break;
            }
        }
        result.extend([value]);
    }
    Some(result)
}

pub(super) fn parse_extended_identifier(
    identifier: &Ident,
    iterator: &mut IntoIter,
) -> (String, Span) {
    // parses an identifier. Identifier are a sequence of letters or punctuation characters (except ; and :) delimited by spaces.
    let mut result = identifier.to_string();
    let iterator_next = iterator.clone();
    let mut span = identifier.span();
    let mut location = span.end();
    for token in iterator_next {
        if token.span().start() != location {
            break;
        }
        location = token.span().end();
        match &token {
            TokenTree::Ident(ident) => {
                result.push_str(&ident.to_string());
                span = span.join(ident.span()).unwrap_or(span);
                iterator.next();
            }
            TokenTree::Punct(punct)
                if punct.as_char() != ':' && punct.as_char() != ';' && punct.as_char() != '=' =>
            {
                result.push_str(&punct.to_string());
                span = span.join(punct.span()).unwrap_or(span);
                iterator.next();
            }
            _ => {
                break;
            }
        }
    }
    (result, span)
}

impl Grammar {
    pub(crate) fn from_dsl(grammar: TokenStream) -> Result<Self> {
        let mut current = grammar.into_iter();
        let mut terminals = Vec::new();
        let mut rules = Vec::new();
        let mut start = None;
        let mut parameters = TokenStream::new();
        while let Some(section) = current.next() {
            match &section {
                TokenTree::Ident(section_name) => match section_name.to_string().as_str() {
                    "terminals" => match consume_parameter(&mut current, true) {
                        None => {
                            return Err(missing_value(section_name, "terminals"));
                        }
                        Some(tree) => {
                            terminals.extend(terminals::from_dsl(tree)?);
                        }
                    },
                    "rules" => match consume_parameter(&mut current, true) {
                        None => {
                            return Err(missing_value(section_name, "rules"));
                        }
                        Some(tree) => {
                            rules.extend(rules::from_dsl(tree)?);
                        }
                    },
                    "start" => {
                        if start.is_some() {
                            return Err(duplicate_section(section_name, "start"));
                        }
                        match consume_parameter(&mut current, true) {
                            None => {
                                return Err(missing_value(section_name, "start"));
                            }
                            Some(tree) => {
                                start = Some(start::from_dsl(tree)?);
                            }
                        }
                    }
                    "variant" => match consume_parameter(&mut current, true) {
                        None => {
                            return Err(missing_value(section_name, "variant"));
                        }
                        Some(tree) => {
                            variants::from_dsl(tree)?;
                        }
                    },
                    "param" => match consume_parameter(&mut current, false) {
                        None => {
                            return Err(missing_value(section_name, "param"));
                        }
                        Some(tree) => {
                            parameters.extend(tree);
                            parameters.extend([TokenTree::Punct(Punct::new(',', Spacing::Alone))]);
                        }
                    },
                    _ => {
                        return Err(invalid_token(
                            section,
                            "Expecting a section `variant`, `terminals`, `rules`, `start`, `param`",
                        ))
                    }
                },
                _ => {
                    return Err(invalid_token(
                        section,
                        "Expecting a section `variant`, `terminals`, `rules`, `start`, `param`",
                    ))
                }
            }
        }

        if terminals.is_empty() {
            return Err(Error::new(
                Span::call_site(),
                "No terminal defined.".to_string(),
            ));
        }

        if rules.is_empty() {
            return Err(Error::new(
                Span::call_site(),
                "No rule defined.".to_string(),
            ));
        }

        rules.sort_by(|a, b| {
            if a.production.is_none() && b.production.is_some() {
                std::cmp::Ordering::Greater
            } else if a.production.is_some() && b.production.is_none() {
                std::cmp::Ordering::Less
            } else {
                std::cmp::Ordering::Equal
            }
        });

        Ok(Grammar {
            parameters,
            terminals,
            rules,
        })
    }
}
