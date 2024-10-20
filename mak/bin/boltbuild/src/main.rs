use boltbuild::application::Application;
use boltbuild::error::Result;

fn try_main() -> Result<()> {
    Application::init()?.run()
}

fn main() {
    use colored::Colorize;
    try_main().unwrap_or_else(|err| match err.location {
        None => println!("{}: {}", "error".red(), err.message.bold()),
        Some(location) => println!(
            "{}:{}: {}: {}",
            location.0,
            location.1,
            "error".red(),
            err.message.bold()
        ),
    })
}
