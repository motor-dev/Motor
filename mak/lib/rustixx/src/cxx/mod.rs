use std::collections::HashMap;
use grammetica::grammar;

struct Calc {
    vars: HashMap<String, i32>,
}

impl Calc {
    grammar! {
        params {
            &mut self
        }
        variants {
            mult: [mult],
        }

        start calculator;

        tokens {
            identifier: String => r"[a-zA-Z_\p{XID_Continue}][a-zA-Z_0-9\p{XID_Continue}]+" { $0.to_str().to_string() },
            number: i64 => r"[0-9]+" { $0.to_str().parse().unwrap() },
            '+',
            '-',
            '=',
            [mult]
            {
                '*',
                '/',
                '%',
            },
        }

        rules {
            calculator: () => statement calculator;
            calculator: () => ;

            statement: () => identifier '=' expression { self.vars.insert($0, $2); }
            statement: () => expression { println!("{}", $0) }

            expression: i64 => number { $0 }
            expression: i64 => number '+' number { $0 + $2 }
            expression: i64 => number '-' number { $0 - $2 }
            expression: i64 => '-' number { - $1 }
            [[mult]]
            {
                expression: i64 => number '*' number { $0 * $2 }
                expression: i64 => number '/' number { $0 / $2 }
                expression: i64 => number '%' number { $0 % $2 }
            }
        }
    }
}
