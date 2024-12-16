mod cxx;

pub fn test() {
    let mut calc = cxx::Calc::new();
    calc.parse()
}