use super::{Error, Grammar, Result};
use proc_macro2::Span;
use quote::{quote, ToTokens};
use std::collections::HashMap;

impl Grammar {
    pub(crate) fn write(&self) -> Result<proc_macro::TokenStream> {
        let terminals = self
            .terminals
            .iter()
            .map(|x| x.name.as_str())
            .collect::<Vec<&str>>();
        let mut types = HashMap::new();
        let mut rules = Vec::new();

        for rule in self.rules.iter() {
            if let Some(ty) = &rule.ty {
                if let Some(existing) =
                    types.insert(rule.name.to_string(), (rule.location, ty.to_token_stream()))
                {
                    return Err(Error::new_with(
                        rule.location,
                        format!("Duplicate type declaration for rule `{}`.", rule.name),
                        Error::new(existing.0, "Previous declaration here.".to_string()),
                    ));
                }
            }
            if let Some(production) = &rule.production {
                rules.push((
                    rule.name.as_str(),
                    production
                        .iter()
                        .map(|x| x.value.as_str())
                        .collect::<Vec<&str>>(),
                ));
            }
        }

        let state_machine = grammetica_lib::make_lr(
            &terminals,
            &rules
                .iter()
                .map(|(x, y)| (*x, y.as_slice()))
                .collect::<Vec<(&str, &[&str])>>(),
        )
        .map_err(|error| self.error_from_lib(error))?;

        let parameters = &self.parameters;
        Ok(quote! {
            pub fn parse(#parameters text: &str) -> () {
            }
        }
        .into())
    }

    fn error_from_lib(&self, error: grammetica_lib::Error) -> Error {
        if let Some(next) = error.next {
            Error::new_with(
                self.span_from_lib(error.location),
                error.message,
                self.error_from_lib(*next),
            )
        } else {
            Error::new(self.span_from_lib(error.location), error.message)
        }
    }

    fn span_from_lib(&self, location: grammetica_lib::Location) -> Span {
        match location {
            grammetica_lib::Location::LexRule(rule) => self.terminals[rule].location,
            grammetica_lib::Location::ParseRule(rule, symbol) => {
                if let Some(symbol) = symbol {
                    self.rules[rule].production.as_ref().unwrap()[symbol].location
                } else {
                    self.rules[rule].location
                }
            }
        }
    }
}
