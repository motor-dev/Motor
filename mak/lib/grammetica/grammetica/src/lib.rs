use crate::error::Error;
use proc_macro::TokenStream;
use quote::quote_spanned;

mod error;
mod parser;

fn raise(error: Error, mut result: proc_macro2::TokenStream) -> proc_macro2::TokenStream {
    let message = error.message.as_str();
    result.extend(quote_spanned! {
        error.location.into() => compile_error!(#message);
    });
    if let Some(note) = error.note {
        result = raise(*note, result);
    }
    result
}

#[proc_macro]
pub fn grammar(rules: TokenStream) -> TokenStream {
    match parser::Grammar::from_dsl(proc_macro2::TokenStream::from(rules)) {
        Ok(grammar) => grammar.write(),
        Err(error) => raise(error, proc_macro2::TokenStream::new()).into(),
    }
}
