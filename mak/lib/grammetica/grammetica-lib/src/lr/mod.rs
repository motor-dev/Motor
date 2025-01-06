use super::diagnostics::{Error, Result};
use std::collections::hash_map::Entry;
use std::collections::HashMap;

pub struct StateMachine<'l> {
    pub names: Vec<&'l str>,
}

pub fn make_lr<'l>(
    terminals: &[&'l str],
    rules: &[(&'l str, &'l [&'l str])],
) -> Result<StateMachine<'l>> {
    let (map_index, names) = build_name_tables(terminals, rules)?;
    Ok(StateMachine { names })
}

fn build_name_tables<'l>(
    terminals: &[&'l str],
    rules: &[(&'l str, &'l [&'l str])],
) -> Result<(HashMap<&'l str, usize>, Vec<&'l str>)> {
    let mut names = Vec::new();
    let mut map_index = HashMap::new();
    for &terminal in terminals {
        match map_index.entry(terminal) {
            Entry::Occupied(entry) => {
                return Err(Error::new_parse_error(
                    0,
                    None,
                    format!("`{}` is already defined", terminal),
                    Some(Error::new_lex_error(
                        *entry.get(),
                        "terminal declared here".to_string(),
                        None,
                    )),
                ));
            }
            Entry::Vacant(entry) => {
                entry.insert(names.len());
                names.push(terminal);
            }
        }
    }

    for &reserved in &["<eof>", "<error>"] {
        match map_index.entry(reserved) {
            Entry::Occupied(entry) => {
                return Err(Error::new_lex_error(
                    *entry.get(),
                    format!("`{}` is a reserved terminal", reserved),
                    None,
                ));
            }
            Entry::Vacant(entry) => {
                entry.insert(names.len());
                names.push(reserved);
            }
        }
    }

    for (rule_index, (nonterminal, _)) in rules.iter().enumerate() {
        match map_index.entry(nonterminal) {
            Entry::Occupied(entry) if *entry.get() < terminals.len() => {
                return Err(Error::new_parse_error(
                    rule_index,
                    None,
                    format!("`{}` is already defined as a terminal", nonterminal),
                    Some(Error::new_lex_error(
                        *entry.get(),
                        "terminal declared here".to_string(),
                        None,
                    )),
                ));
            }
            Entry::Occupied(entry) if *entry.get() < terminals.len() + 2 => {
                return Err(Error::new_parse_error(
                    rule_index,
                    None,
                    format!("`{}` is a reserved terminal name", nonterminal),
                    Some(Error::new_lex_error(
                        *entry.get(),
                        "reserved terminal declared here".to_string(),
                        None,
                    )),
                ));
            }
            Entry::Occupied(_) => (),
            Entry::Vacant(entry) => {
                entry.insert(names.len());
                names.push(nonterminal);
            }
        }
    }
    Ok((map_index, names))
}