use crate::error::{Error, Result};
use proc_macro2::token_stream::IntoIter;
use proc_macro2::{Delimiter, Group, Ident, Punct, Spacing, Span, TokenStream, TokenTree};
use quote::ToTokens;

mod rules;
mod start;
mod terminals;
mod variants;

use terminals::Terminal;

pub(super) struct Grammar {
    parameters: TokenTree,
    terminals: Vec<Terminal>,
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
    identifier: &TokenTree,
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
    pub(crate) fn write(&self) -> proc_macro::TokenStream {
        let mut result = "pub fn parse".parse::<proc_macro::TokenStream>().unwrap();
        result.extend([proc_macro::TokenStream::from(
            self.parameters.to_token_stream(),
        )]);
        result.extend(" -> () {}".parse::<proc_macro::TokenStream>().unwrap());
        result
    }

    pub(crate) fn from_dsl(grammar: TokenStream) -> Result<Self> {
        let mut current = grammar.into_iter();
        let mut terminals = None;
        let mut rules = None;
        let mut start = None;
        let mut parameters: Option<TokenStream> = None;
        while let Some(section) = current.next() {
            match &section {
                TokenTree::Ident(section_name) => match section_name.to_string().as_str() {
                    "terminals" => {
                        if terminals.is_some() {
                            return Err(duplicate_section(section_name, "terminals"));
                        }
                        match consume_parameter(&mut current, true) {
                            None => {
                                return Err(missing_value(section_name, "terminals"));
                            }
                            Some(tree) => {
                                terminals = Some(terminals::from_dsl(tree)?);
                            }
                        }
                    }
                    "rules" => {
                        if rules.is_some() {
                            return Err(duplicate_section(section_name, "rules"));
                        }
                        match consume_parameter(&mut current, true) {
                            None => {
                                return Err(missing_value(section_name, "rules"));
                            }
                            Some(tree) => {
                                rules = Some(rules::from_dsl(tree)?);
                            }
                        }
                    }
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
                            if let Some(param_list) = &mut parameters {
                                param_list
                                    .extend([TokenTree::Punct(Punct::new(',', Spacing::Alone))]);
                                param_list.extend(tree);
                            } else {
                                parameters = Some(tree);
                            }
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
        if terminals.is_none() {
            return Err(Error::new(
                Span::call_site(),
                "Missing required section `terminals`.".to_string(),
            ));
        }

        Ok(Grammar {
            parameters: TokenTree::Group(Group::new(
                Delimiter::Parenthesis,
                parameters.unwrap_or_default(),
            )),
            terminals: terminals.unwrap(),
        })
    }
}
