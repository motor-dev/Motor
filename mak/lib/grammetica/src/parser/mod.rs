use proc_macro::{Delimiter, Group, Ident, TokenStream, TokenTree};
use std::option::IntoIter;
use crate::error::{Error, Result};

mod start;
mod tokens;
mod rules;
mod params;
mod variants;

pub(crate) struct Grammar {}

fn invalid_token(token: TokenTree, expected: &str) -> Error {
    match token {
        TokenTree::Ident(ident) =>
            Error::new(ident.span(), format!("Unexpected identifier `{}`. {}.", ident, expected)),
        TokenTree::Punct(punct) =>
            Error::new(punct.span(), format!("Unexpected token `{}`. {}.", punct, expected)),
        TokenTree::Literal(literal) =>
            Error::new(literal.span(), format!("Unexpected literal `{}`. {}.", literal, expected)),
        TokenTree::Group(group) =>
            Error::new(group.span_open(), format!("Unexpected {} block. {}.", match group.delimiter() {
                Delimiter::Brace => "{}",
                Delimiter::Parenthesis => "()",
                Delimiter::Bracket => "[]",
                Delimiter::None => "macro",
            }, expected)),
    }
}

fn duplicate_section(token: &Ident, section: &str) -> Error {
    Error::new(token.span(), format!("Section `{}`already defined.", section))
}

fn missing_value(token: &Ident, section: &str) -> Error {
    Error::new(token.span(), format!("Unexpected end of input: expected a value for section `{}`.", section))
}


fn consume_parameter(iterator: &mut proc_macro::token_stream::IntoIter) -> Option<TokenStream> {
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
            if punct.as_char() == ':' {
                break
            }
        }
        result.extend([value]);
    }
    Some(result)
}

impl Grammar {
    pub(crate) fn from_dsl(grammar: TokenStream) -> Result<Self> {
        let mut current = grammar.into_iter();
        let mut tokens = None;
        let mut rules = None;
        let mut start = None;
        let mut variants = None;
        let mut params = None;
        while let Some(section) = current.next() {
            match &section {
                TokenTree::Ident(section_name) => {
                    match section_name.to_string().as_str() {
                        "tokens" => {
                            if tokens.is_some() {
                                return Err(duplicate_section(section_name, "tokens"));
                            }
                            match consume_parameter(&mut current) {
                                None => {
                                    return Err(missing_value(section_name, "tokens"));
                                },
                                Some(tree) => {
                                    tokens = Some(tokens::from_dsl(tree)?);
                                }
                                
                            }
                        }
                        "rules" => {
                            if rules.is_some() {
                                return Err(duplicate_section(section_name, "rules"));
                            }
                            match consume_parameter(&mut current) {
                                None => {
                                    return Err(missing_value(section_name, "rules"));
                                },
                                Some(tree) => {
                                    rules = Some(rules::from_dsl(tree)?);
                                }

                            }
                        }
                        "start" => {
                            if start.is_some() {
                                return Err(duplicate_section(section_name, "start"));
                            }
                            match consume_parameter(&mut current) {
                                None => {
                                    return Err(missing_value(section_name, "start"));
                                },
                                Some(tree) => {
                                    start = Some(start::from_dsl(tree)?);
                                }

                            }
                        }
                        "variants" => {
                            if variants.is_some() {
                                return Err(duplicate_section(section_name, "variants"));
                            }
                            match consume_parameter(&mut current) {
                                None => {
                                    return Err(missing_value(section_name, "variants"));
                                },
                                Some(tree) => {
                                    variants = Some(variants::from_dsl(tree)?);
                                }

                            }
                        }
                        "params" => {
                            if params.is_some() {
                                return Err(duplicate_section(section_name, "params"));
                            }
                            match consume_parameter(&mut current) {
                                None => {
                                    return Err(missing_value(section_name, "params"));
                                },
                                Some(tree) => {
                                    params = Some(params::from_dsl(tree)?);
                                }

                            }
                        }
                        _ => return Err(invalid_token(section, "Expecting a section `variants`, `tokens`, `rules`, `start`, `params`"))
                    }
                }
                _ => return Err(invalid_token(section, "Expecting a section `variants`, `tokens`, `rules`, `start`, `params`"))
            }
        }
        Ok(Grammar {})
    }
}

