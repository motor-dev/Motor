use crate::{Error, Result};

pub(crate) enum CharClass {
    Char(char),
    Range(Vec<(char, char)>),
    ComplementRange(Vec<(char, char)>),
    Group(Vec<Item>),
    Or(Box<CharClass>, Box<CharClass>),
}

pub(crate) struct Item {
    value: CharClass,
    repeat: (usize, usize),
}

pub(crate) fn make_regexp(r: &str, index: usize) -> Result<Vec<Item>> {
    let mut sequence = Vec::new();
    let mut current = r.chars();
    let mut offset = 0;
    if let Some(c) = current.next() {
        offset += 1;
        let mut class = Some(match c {
            '[' => {
                parse_char_class(&mut current, index, &mut offset)?;
            }
            '(' => {}
            '\\' => {}
            '?' => {}
            '*' => {}
            '+' => {}
            _ => {}
        });
        while let Some(c) = current.next() {
            offset += 1;
            match c {
                '[' => {
                    parse_char_class(&mut current, index, &mut offset)?;
                }
                '(' => {}
                '\\' => {}
                '?' => {}
                '*' => {}
                '+' => {}
                _ => {}
            }
        }
    }
    Ok(sequence)
}

fn parse_char_class(
    current: &mut std::str::Chars,
    index: usize,
    offset: &mut usize,
) -> Result<CharClass> {
    //let mut ranges = Vec::new();
    let start = *offset;
    let mut complement = false;

    while let Some(c) = current.next() {
        *offset += 1;
        match c {
            '^' => {
                complement = true;
                continue;
            }
            ']' => {
                return Err(Error::new_lex_error(
                    index,
                    Some((start, *offset)),
                    "Empty character set".into(),
                    None,
                ));
            }
            _ => {}
        }
    }
    Err(Error::new_lex_error(
        index,
        Some((start, *offset)),
        "missing ] to close character set".into(),
        None,
    ))
}
