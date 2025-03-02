mod regex;

pub struct StateMachine<'l> {
    pub names: Vec<&'l str>,
}

pub fn make_tokenizer<'l>(terminals: &[&'l str]) -> crate::Result<StateMachine<'l>> {
    for (index, terminal) in terminals.iter().enumerate() {
        let regexp = regex::make_regexp(terminal, index)?;
    }
    Ok(StateMachine{ names: vec![] })
}
