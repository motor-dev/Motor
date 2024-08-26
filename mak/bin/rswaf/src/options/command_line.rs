use super::CommandLineParser;
use clap::ArgAction;
use crate::environment::{Environment, EnvironmentValue};

struct Interface {
    long: Option<String>,
    short: Option<String>,
    category: Option<String>,
    help: String,
    required: bool,
    choice_list: Option<Vec<String>>,
    action: ArgAction,
}

pub(super) struct Argument {
    pub(super) name: String,
    interface: Option<Interface>,
    pub(super) default: EnvironmentValue,
}

impl CommandLineParser {
    pub(crate) fn new() -> Self {
        Self {
            options: Vec::new(),
        }
    }

    pub(crate) fn get_value(&self, name: &str) -> mlua::Result<EnvironmentValue> {
        if let Some(index) = self.options.iter().position(|x| x.name.eq(name)) {
            Ok(self.options[index].default.clone())
        } else {
            Err(mlua::Error::RuntimeError(
                format!("'{}': no option registered with this name", name).to_string(),
            ))
        }
    }

    pub(crate) fn add_setting(
        self: &mut Self,
        name: String,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        if let Some(_) = self.options.iter().position(|x| x.name.eq(&name)) {
            Err(mlua::Error::RuntimeError(
                format!(
                    "'{}': an option is already registered with this name",
                    &name
                )
                    .to_string(),
            ))
        } else {
            self.options.push(Argument {
                name,
                interface: None,
                default,
            });
            Ok(())
        }
    }

    fn add_option(
        self: &mut Self,
        name: String,
        help: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        required: bool,
        default: EnvironmentValue,
        choice_list: Option<Vec<String>>,
        action: ArgAction,
    ) -> mlua::Result<()> {
        if let Some(_) = self.options.iter().position(|x| x.name.eq(&name)) {
            Err(mlua::Error::RuntimeError(
                format!(
                    "'{}': an option is already registered with this name",
                    &name
                )
                    .to_string(),
            ))
        } else {
            self.options.push(Argument {
                name,
                interface: Some(Interface {
                    long,
                    short,
                    category,
                    help,
                    required,
                    choice_list,
                    action,
                }),
                default,
            });
            Ok(())
        }
    }

    pub(crate) fn add_flag(
        self: &mut Self,
        name: String,
        help: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            help,
            category,
            long,
            short,
            required,
            default,
            None,
            ArgAction::SetTrue,
        )
    }

    pub(crate) fn add_value(
        self: &mut Self,
        name: String,
        help: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            help,
            category,
            long,
            short,
            required,
            default,
            None,
            ArgAction::Set,
        )
    }

    pub(crate) fn add_count(
        self: &mut Self,
        name: String,
        help: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            help,
            category,
            long,
            short,
            required,
            default,
            None,
            ArgAction::Count,
        )
    }

    pub(crate) fn add_choice(
        self: &mut Self,
        name: String,
        help: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        required: bool,
        choice_list: Vec<String>,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            help,
            category,
            long,
            short,
            required,
            default,
            Some(choice_list),
            ArgAction::Set,
        )
    }

    pub(crate) fn add_list(
        self: &mut Self,
        name: String,
        help: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            help,
            category,
            long,
            short,
            required,
            default,
            None,
            ArgAction::Append,
        )
    }

    pub(crate) fn parse_command_line(self: &Self) -> Environment {
        let mut env = Environment::new();
        for option in &self.options {
            env.set(option.name.as_str(), option.default.clone());
        }
        self.parse_command_line_into(&mut env);
        env
    }

    pub(crate) fn parse_command_line_into(self: &Self, env: &mut Environment) {
        use clap::{Arg, Command, builder::PossibleValuesParser, builder::PossibleValue};
        let mut cmd = Command::new("rswaf");
        for option in &self.options {
            if let Some(interface) = &option.interface {
                let mut arg = Arg::new(&option.name);
                if let Some(category) = &interface.category {
                    arg = arg.help_heading(category);
                }
                if let Some(long) = &interface.long {
                    arg = arg.long(long);
                }
                if let Some(short) = &interface.short {
                    arg = arg.short(short.chars().next().unwrap());
                }
                if let Some(choice) = &interface.choice_list {
                    arg = arg.value_parser(PossibleValuesParser::new(choice.iter().map(|x| PossibleValue::new(x)).collect::<Vec<PossibleValue>>()));
                }
                arg = arg.help(&interface.help);
                arg = arg.action(interface.action.clone());
                arg = arg.required(interface.required);
                cmd = cmd.arg(arg);
            }
        }

        let matches = cmd.get_matches();
        for option in &self.options {
            if let Some(interface) = &option.interface {
                if matches.contains_id(option.name.as_str()) {
                    match interface.action {
                        ArgAction::SetTrue => env.set(
                            option.name.as_str(),
                            EnvironmentValue::Bool(matches.get_flag(option.name.as_str())),
                        ),
                        ArgAction::Set => env.set(
                            option.name.as_str(),
                            EnvironmentValue::String(
                                matches
                                    .get_one::<String>(option.name.as_str())
                                    .unwrap()
                                    .to_string(),
                            ),
                        ),
                        ArgAction::Count => env.set(
                            option.name.as_str(),
                            EnvironmentValue::Integer(
                                matches.get_count(option.name.as_str()).into(),
                            ),
                        ),
                        ArgAction::Append => {
                            let mut vec = Vec::<EnvironmentValue>::new();
                            for m in matches.get_many::<String>(option.name.as_str()).unwrap() {
                                vec.push(EnvironmentValue::String(m.clone()));
                            }
                            env.set(option.name.as_str(), EnvironmentValue::Vec(vec))
                        }
                        _ => panic!("unknown option type"),
                    }
                }
            }
        }
    }
}