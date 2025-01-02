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
        start calculator;

        terminals {
            identifier: String => r"\p{XID_Start}\p{XID_Continue}*" { $0.to_str().to_string() }
            number: i64 => r"[0-9]+" { $0.to_str().parse().unwrap() }
            "+";
            "-";
            "=";
            [feature:mult]
            {
                "*";
                "/";
                "%";
            }
        }

        rules {
            calculator : ();
            calculator => statement calculator;
            calculator => ;

            statement: ();
            statement => identifier "=" expression ";" { self.vars.insert($0, $2); }
            statement => expression ";" { println!("{}", $0) }

            expression: i64;
            expression => identifier { self.vars.get($0).unwrap(); }
            expression => number;
            expression => number + number { $0 + $2 }
            expression => number - number { $0 - $2 }
            expression => "-" number { - $1 }
            [feature:mult]
            {
                expression => number * number { $0 * $2 }
                expression => number / number { $0 / $2 }
                expression => number % number { $0 % $2 }
            }
        }
    }
}
