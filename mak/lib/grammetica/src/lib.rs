use quote::quote_spanned;
use proc_macro::TokenStream;
use crate::error::Error;

mod glr;
mod parser;
mod error;

fn raise(error: Error, mut result: proc_macro2::TokenStream) -> proc_macro2::TokenStream {
    let message = error.message.as_str();
    result.extend(quote_spanned! {
        error.location.into() => compile_error!(#message);
    });
    result
}

#[proc_macro]
pub fn grammar(rules: TokenStream) -> TokenStream {
    match parser::Grammar::from_dsl(rules) {
        Ok(grammar) => {
            let mut result = "fn parse".parse::<TokenStream>().unwrap();
            result.extend([grammar.parameters]);
            result.extend(" -> () {}".parse::<TokenStream>().unwrap());
            result
        }
        Err(error) => raise(error, proc_macro2::TokenStream::new()).into()
    }
}
