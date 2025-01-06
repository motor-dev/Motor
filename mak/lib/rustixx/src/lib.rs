mod cxx;

pub fn test() {
    let mut calc = cxx::Calc::new();
    calc.parse("1 + 2 * 3");
}