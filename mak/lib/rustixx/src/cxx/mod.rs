use grammetica::grammar;
//use std::collections::HashMap;

pub struct Calc {
    //vars: HashMap<String, i32>,
}

impl Calc {
    pub fn new() -> Self {
        Self {
            //vars: HashMap::new(),
        }
    }

    grammar! {
        param &mut self;
        variant mult [mult];
        variant mult [mult];

        start calculator;

        tokens {
            identifier: String => r"[a-zA-Z_\p{XID_Continue}][a-zA-Z_0-9\p{XID_Continue}]+" { $0.to_str().to_string() }
            number: i64 => r"[0-9]+" { $0.to_str().parse().unwrap() }
            "+";
            "-";
            "=";
            [mult]
            {
                '*';
                '/';
                '%';
            }
        }

        rules {
            calculator: ();
            calculator => statement calculator;
            calculator => ;

            statement: ();
            statement => identifier '=' expression ';' { self.vars.insert($0, $2); }
            statement => expression ';' { println!("{}", $0) }

            expression: i64;
            expression => identifier { self.vars.get($0).unwrap(); }
            expression => number { $0 }
            expression => number '+' number { $0 + $2 }
            expression => number '-' number { $0 - $2 }
            expression => '-' number { - $1 }
            [variant:mult]
            {
                expression => number '*' number { $0 * $2 }
                expression => number '/' number { $0 / $2 }
                expression => number '%' number { $0 % $2 }
            }
        }
    }
}
