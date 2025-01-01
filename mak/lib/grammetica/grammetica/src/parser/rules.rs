use super::{parse_extended_identifier, Error, Result};
use proc_macro2::token_stream::IntoIter;
use proc_macro2::{Delimiter, Spacing, Span, TokenStream, TokenTree};

pub(super) fn from_dsl(grammar: TokenStream) -> Result<()> {
    let mut grammar = grammar.into_iter();
    while let Some(ident) = grammar.next() {
        match &ident {
            TokenTree::Ident(_) => {
                parse_rule(ident, &mut grammar)?;
            }
            TokenTree::Punct(_) => {
                parse_rule(ident, &mut grammar)?;
            }
            TokenTree::Group(group) if group.delimiter() == Delimiter::Bracket => loop {
                match grammar.next() {
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Bracket => {
                        continue;
                    }
                    Some(TokenTree::Group(group)) if group.delimiter() == Delimiter::Brace => {
                        from_dsl(group.stream())?;
                        break;
                    }
                    Some(ident) => match &ident {
                        TokenTree::Ident(_) => {
                            parse_rule(ident, &mut grammar)?;
                        }
                        TokenTree::Punct(_) => {
                            parse_rule(ident, &mut grammar)?;
                        }
                        _ => {
                            return Err(Error::new(
                                ident.span(),
                                "Unexpected token after variant tag".to_string(),
                            ));
                        }
                    },
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
                    ident.span(),
                    format!("Unexpected token {:?} in rule section", ident),
                ));
            }
        }
    }
    Ok(())
}

fn parse_rule(identifier: TokenTree, rule: &mut IntoIter) -> Result<()> {
    //let mut result_type = None;
    let (_, span) = parse_extended_identifier(&identifier, rule);
    match rule.next() {
        Some(TokenTree::Punct(punct)) if punct.as_char() == ':' => parse_typed_rule(span, rule),
        Some(TokenTree::Punct(punct))
            if punct.as_char() == '=' && punct.spacing() == Spacing::Joint =>
        {
            parse_untyped_rule(span, rule)
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

fn parse_typed_rule(location: Span, rule: &mut IntoIter) -> Result<()> {
    let t = rule.next();
    if t.is_none() {
        return Err(Error::new(
            location,
            "Unexpected end of input after `:`: expected a type".to_string(),
        ));
    }
    let result_type = t.unwrap();

    match rule.next() {
        None => Err(Error::new(
            result_type.span(),
            "Unexpected end of input after type: expected a rule".to_string(),
        )),
        Some(TokenTree::Punct(p)) if p.as_char() == ';' => Ok(()),
        Some(TokenTree::Punct(p)) if p.as_char() == '=' && p.spacing() == Spacing::Joint => {
            parse_untyped_rule(location, rule)
        }
        Some(other) => Err(Error::new(
            other.span(),
            "Unexpected token after type: expected `;` or `=>`".to_string(),
        )),
    }
}

fn parse_untyped_rule(location: Span, rule: &mut IntoIter) -> Result<()> {
    match rule.next() {
        None => Err(Error::new(
            location,
            "Unexpected end of input after `=`: expected `=>`".to_string(),
        )),
        Some(TokenTree::Punct(p)) if p.as_char() == '>' => parse_expansion(rule),
        Some(other) => Err(Error::new(
            other.span(),
            "Unexpected token after `=`: expected `=>`".to_string(),
        )),
    }
}

fn parse_expansion(rule: &mut IntoIter) -> Result<()> {
    for token in rule {
        match token {
            TokenTree::Ident(_) => {}
            TokenTree::Literal(_) => {}
            TokenTree::Group(group) if group.delimiter() == Delimiter::Bracket => {}
            TokenTree::Group(group) if group.delimiter() == Delimiter::Brace => {
                break;
            }
            TokenTree::Punct(punct) if punct.as_char() == ';' => {
                break;
            }
            _ => {
                return Err(Error::new(
                    token.span(),
                    format!("Unexpected token `{:?}` in rule section", token),
                ));
            }
        }
    }
    Ok(())
}
