use crossterm::tty::IsTty;
use crossterm::QueueableCommand;
use crossterm::{cursor, style, terminal};
use std::io::{Stdout, Write};

pub(crate) struct Logger {
    output: Stdout,
    depth: u32,
    width: usize,
    use_colors: bool,
    status: Option<Vec<StatusCommand>>,
}

impl Logger {
    pub(crate) fn new(use_colors: Option<bool>) -> Self {
        let stdout = std::io::stdout();
        let use_colors = use_colors.or(Some(stdout.is_tty())).unwrap();
        Self {
            output: stdout,
            depth: 0,
            width: 20,
            use_colors,
            status: None,
        }
    }

    pub(crate) fn begin(&mut self, message: &str) {
        if self.depth == 0 {
            if message.len() >= self.width {
                self.width = message.len() + 1;
            }
            let message = format!("{}{}: ", message, " ".repeat(self.width - message.len()));
            self.log(message.as_str(), false);
        }
        self.depth += 1;
    }

    pub(crate) fn end(&mut self, message: &str, success: bool) {
        self.depth -= 1;
        if self.depth == 0 {
            if self.use_colors {
                self.output
                    .queue(style::SetForegroundColor(if success {
                        style::Color::Green
                    } else {
                        style::Color::Yellow
                    }))
                    .unwrap()
                    .queue(style::Print(message))
                    .unwrap()
                    .queue(style::SetForegroundColor(style::Color::Reset))
                    .unwrap();
            } else {
                self.output
                    .queue(style::Print(message))
                    .unwrap();
            }
            self.log("", true);
        }
    }

    pub(crate) fn debug(&mut self, message: &str) {
        if self.depth == 0 {
            self.log(message, true);
        }
    }

    pub(crate) fn warning(&mut self, message: &str) {
        if self.depth == 0 {
            if self.use_colors {
                self.output
                    .queue(style::SetForegroundColor(style::Color::Yellow))
                    .unwrap()
                    .queue(style::Print("warn: "))
                    .unwrap()
                    .queue(style::SetForegroundColor(style::Color::Reset))
                    .unwrap();
            } else {
                self.output.queue(style::Print("warn: ")).unwrap();
            }
            self.log(message, true);
        }
    }

    pub(crate) fn error(&mut self, message: &str) {
        if self.depth == 0 {
            if self.use_colors {
                self.output
                    .queue(style::SetForegroundColor(style::Color::Red))
                    .unwrap()
                    .queue(style::Print("error: "))
                    .unwrap()
                    .queue(style::SetForegroundColor(style::Color::Reset))
                    .unwrap();
            } else {
                self.output.queue(style::Print("error: ")).unwrap();
            }
            self.log(message, true);
        }
    }

    pub(crate) fn set_status(&mut self, message: &str) {
        if self.use_colors && self.status.is_none() {
            self.output
                .queue(cursor::MoveDown(1))
                .unwrap()
                .queue(cursor::MoveUp(1))
                .unwrap();
        }
        self.status = Some(StatusCommand::parse(message));
        self.log("", false);
    }

    pub(crate) fn clear_status(&mut self) {
        if self.use_colors && self.status.is_some() {
            self.output
                .queue(cursor::MoveDown(1))
                .unwrap()
                .queue(terminal::Clear(terminal::ClearType::CurrentLine))
                .unwrap()
                .queue(cursor::MoveUp(1))
                .unwrap()
                .flush()
                .unwrap();
        }
        self.status = None;
    }

    fn log(&mut self, message: &str, mut add_newline: bool) {
        if self.use_colors && self.status.is_some() {
            if !add_newline {
                add_newline = message.as_bytes().iter().filter(|&&c| c == b'\n').count() != 0;
            }
            if add_newline {
                self.output
                    .queue(cursor::SavePosition)
                    .unwrap()
                    .queue(cursor::MoveDown(1))
                    .unwrap()
                    .queue(terminal::Clear(terminal::ClearType::CurrentLine))
                    .unwrap()
                    .queue(cursor::RestorePosition)
                    .unwrap();
            }
        }
        self.output.queue(style::Print(message)).unwrap();
        if add_newline {
            self.output.queue(style::Print("\n")).unwrap();
        }
        if self.use_colors && self.status.is_some() {
            self.output
                .queue(cursor::SavePosition)
                .unwrap()
                .queue(cursor::MoveToNextLine(1))
                .unwrap();
            for cmd in self.status.as_mut().unwrap() {
                cmd.write(&mut self.output);
            }

            self.output.queue(cursor::RestorePosition).unwrap();
        }
        self.output.flush().unwrap();
    }
}

pub(crate) enum StatusCommand {
    Text(String),
    FgReset,
    FgDarkGrey,
    FgRed,
    FgGreen,
    FgYellow,
    FgBlue,
    FgMagenta,
    FgCyan,
    FgWhite,
    FgBlack,
    FgDarkRed,
    FgDarkGreen,
    FgDarkYellow,
    FgDarkBlue,
    FgDarkMagenta,
    FgDarkCyan,
    FgGrey,
    BgReset,
    BgDarkGrey,
    BgRed,
    BgGreen,
    BgYellow,
    BgBlue,
    BgMagenta,
    BgCyan,
    BgWhite,
    BgBlack,
    BgDarkRed,
    BgDarkGreen,
    BgDarkYellow,
    BgDarkBlue,
    BgDarkMagenta,
    BgDarkCyan,
    BgGrey,
}

impl StatusCommand {
    fn parse(message: &str) -> Vec<StatusCommand> {
        let mut result = Vec::new();
        let re = regex::Regex::new(r"\{[a-zA-Z]*}").unwrap();
        let mut start = 0_usize;
        for m in re.find_iter(message) {
            let (match_start, match_end) = (m.start(), m.end());
            if match_start != start {
                result.push(StatusCommand::Text(message[start..match_start].to_string()));
            }
            if let Ok(color) = message[match_start + 1..match_end - 1].parse::<StatusCommand>() {
                result.push(color);
            } else {
                result.push(StatusCommand::Text(
                    message[match_start..match_end].to_string(),
                ));
            }
            start = match_end;
        }
        if start != message.len() {
            result.push(StatusCommand::Text(message[start..].to_string()));
        }
        result
    }

    fn write<'a>(&'a self, out: &'a mut Stdout) -> &mut Stdout {
        match &self {
            StatusCommand::Text(s) => out.queue(style::Print(s.as_str())).unwrap(),
            StatusCommand::FgReset => out
                .queue(style::SetForegroundColor(style::Color::Reset))
                .unwrap(),
            StatusCommand::FgDarkGrey => out
                .queue(style::SetForegroundColor(style::Color::DarkGrey))
                .unwrap(),
            StatusCommand::FgRed => out
                .queue(style::SetForegroundColor(style::Color::Red))
                .unwrap(),
            StatusCommand::FgGreen => out
                .queue(style::SetForegroundColor(style::Color::Green))
                .unwrap(),
            StatusCommand::FgYellow => out
                .queue(style::SetForegroundColor(style::Color::Yellow))
                .unwrap(),
            StatusCommand::FgBlue => out
                .queue(style::SetForegroundColor(style::Color::Blue))
                .unwrap(),
            StatusCommand::FgMagenta => out
                .queue(style::SetForegroundColor(style::Color::Magenta))
                .unwrap(),
            StatusCommand::FgCyan => out
                .queue(style::SetForegroundColor(style::Color::Cyan))
                .unwrap(),
            StatusCommand::FgWhite => out
                .queue(style::SetForegroundColor(style::Color::White))
                .unwrap(),
            StatusCommand::FgBlack => out
                .queue(style::SetForegroundColor(style::Color::Black))
                .unwrap(),
            StatusCommand::FgDarkRed => out
                .queue(style::SetForegroundColor(style::Color::DarkRed))
                .unwrap(),
            StatusCommand::FgDarkGreen => out
                .queue(style::SetForegroundColor(style::Color::DarkGreen))
                .unwrap(),
            StatusCommand::FgDarkYellow => out
                .queue(style::SetForegroundColor(style::Color::DarkYellow))
                .unwrap(),
            StatusCommand::FgDarkBlue => out
                .queue(style::SetForegroundColor(style::Color::DarkBlue))
                .unwrap(),
            StatusCommand::FgDarkMagenta => out
                .queue(style::SetForegroundColor(style::Color::DarkMagenta))
                .unwrap(),
            StatusCommand::FgDarkCyan => out
                .queue(style::SetForegroundColor(style::Color::DarkCyan))
                .unwrap(),
            StatusCommand::FgGrey => out
                .queue(style::SetForegroundColor(style::Color::Grey))
                .unwrap(),
            StatusCommand::BgReset => out
                .queue(style::SetBackgroundColor(style::Color::Reset))
                .unwrap(),
            StatusCommand::BgDarkGrey => out
                .queue(style::SetBackgroundColor(style::Color::DarkGrey))
                .unwrap(),
            StatusCommand::BgRed => out
                .queue(style::SetBackgroundColor(style::Color::Red))
                .unwrap(),
            StatusCommand::BgGreen => out
                .queue(style::SetBackgroundColor(style::Color::Green))
                .unwrap(),
            StatusCommand::BgYellow => out
                .queue(style::SetBackgroundColor(style::Color::Yellow))
                .unwrap(),
            StatusCommand::BgBlue => out
                .queue(style::SetBackgroundColor(style::Color::Blue))
                .unwrap(),
            StatusCommand::BgMagenta => out
                .queue(style::SetBackgroundColor(style::Color::Magenta))
                .unwrap(),
            StatusCommand::BgCyan => out
                .queue(style::SetBackgroundColor(style::Color::Cyan))
                .unwrap(),
            StatusCommand::BgWhite => out
                .queue(style::SetBackgroundColor(style::Color::White))
                .unwrap(),
            StatusCommand::BgBlack => out
                .queue(style::SetBackgroundColor(style::Color::Black))
                .unwrap(),
            StatusCommand::BgDarkRed => out
                .queue(style::SetBackgroundColor(style::Color::DarkRed))
                .unwrap(),
            StatusCommand::BgDarkGreen => out
                .queue(style::SetBackgroundColor(style::Color::DarkGreen))
                .unwrap(),
            StatusCommand::BgDarkYellow => out
                .queue(style::SetBackgroundColor(style::Color::DarkYellow))
                .unwrap(),
            StatusCommand::BgDarkBlue => out
                .queue(style::SetBackgroundColor(style::Color::DarkBlue))
                .unwrap(),
            StatusCommand::BgDarkMagenta => out
                .queue(style::SetBackgroundColor(style::Color::DarkMagenta))
                .unwrap(),
            StatusCommand::BgDarkCyan => out
                .queue(style::SetBackgroundColor(style::Color::DarkCyan))
                .unwrap(),
            StatusCommand::BgGrey => out
                .queue(style::SetBackgroundColor(style::Color::Grey))
                .unwrap(),
        }
    }
}

impl std::str::FromStr for StatusCommand {
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "reset" => Ok(StatusCommand::FgReset),
            "dark_grey" => Ok(StatusCommand::FgDarkGrey),
            "red" => Ok(StatusCommand::FgRed),
            "green" => Ok(StatusCommand::FgGreen),
            "yellow" => Ok(StatusCommand::FgYellow),
            "blue" => Ok(StatusCommand::FgBlue),
            "magenta" => Ok(StatusCommand::FgMagenta),
            "cyan" => Ok(StatusCommand::FgCyan),
            "white" => Ok(StatusCommand::FgWhite),
            "black" => Ok(StatusCommand::FgBlack),
            "dark_red" => Ok(StatusCommand::FgDarkRed),
            "dark_green" => Ok(StatusCommand::FgDarkGreen),
            "dark_yellow" => Ok(StatusCommand::FgDarkYellow),
            "dark_blue" => Ok(StatusCommand::FgDarkBlue),
            "dark_magenta" => Ok(StatusCommand::FgDarkMagenta),
            "dark_cyan" => Ok(StatusCommand::FgDarkCyan),
            "grey" => Ok(StatusCommand::FgGrey),
            "bg:reset" => Ok(StatusCommand::BgReset),
            "bg:dark_grey" => Ok(StatusCommand::BgDarkGrey),
            "bg:red" => Ok(StatusCommand::BgRed),
            "bg:green" => Ok(StatusCommand::BgGreen),
            "bg:yellow" => Ok(StatusCommand::BgYellow),
            "bg:blue" => Ok(StatusCommand::BgBlue),
            "bg:magenta" => Ok(StatusCommand::BgMagenta),
            "bg:cyan" => Ok(StatusCommand::BgCyan),
            "bg:white" => Ok(StatusCommand::BgWhite),
            "bg:black" => Ok(StatusCommand::BgBlack),
            "bg:dark_red" => Ok(StatusCommand::BgDarkRed),
            "bg:dark_green" => Ok(StatusCommand::BgDarkGreen),
            "bg:dark_yellow" => Ok(StatusCommand::BgDarkYellow),
            "bg:dark_blue" => Ok(StatusCommand::BgDarkBlue),
            "bg:dark_magenta" => Ok(StatusCommand::BgDarkMagenta),
            "bg:dark_cyan" => Ok(StatusCommand::BgDarkCyan),
            "bg:grey" => Ok(StatusCommand::BgGrey),
            _ => Err(()),
        }
    }
}
