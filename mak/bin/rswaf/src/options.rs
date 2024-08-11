use crate::environment::{Environment, EnvironmentValue};
use clap::ArgAction;
use mlua::{IntoLua, MetaMethod, UserData, UserDataMethods};
use std::sync::{Arc, Mutex};

#[derive(Clone)]
pub(crate) enum Options {
    CommandLineParser(Arc<Mutex<CommandLineParser>>),
    Environment(Arc<Mutex<Environment>>),
}

impl Options {
    pub(crate) fn from_parser(context: Arc<Mutex<CommandLineParser>>) -> Self {
        Options::CommandLineParser(context)
    }
    pub(crate) fn from_env(env: Arc<Mutex<Environment>>) -> Self {
        Options::Environment(env)
    }
}

struct Interface {
    long: Option<String>,
    short: Option<String>,
    category: Option<String>,
    help: String,
    required: bool,
    choice_list: Option<Vec<String>>,
    action: ArgAction,
}

struct Argument {
    name: String,
    interface: Option<Interface>,
    default: EnvironmentValue,
}

pub(crate) struct CommandLineParser {
    options: Vec<Argument>,
}

impl CommandLineParser {
    pub(crate) fn new() -> Self {
        Self {
            options: Vec::new(),
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

impl UserData for CommandLineParser {
    fn add_methods<'lua, M: UserDataMethods<'lua, Self>>(methods: &mut M) {
        methods.add_meta_method_mut(
            MetaMethod::NewIndex,
            |_lua, this, (key, value): (String, mlua::Value)| -> mlua::Result<()> {
                if let Some(index) = this.options.iter().position(|x| x.name.eq(&key)) {
                    this.options[index].default = EnvironmentValue::from_lua(&value)?;
                    Ok(())
                } else {
                    Err(mlua::Error::RuntimeError(
                        format!("'{}': no option registered with this name", key).to_string(),
                    ))
                }
            },
        );
        methods.add_meta_method_mut(
            MetaMethod::Index,
            |lua, this, key: String| -> mlua::Result<mlua::Value> {
                if let Some(index) = this.options.iter().position(|x| x.name.eq(&key)) {
                    this.options[index].default.into_lua(lua)
                } else {
                    Err(mlua::Error::RuntimeError(
                        format!("'{}': no option registered with this name", key).to_string(),
                    ))
                }
            },
        );
        methods.add_method_mut(
            "add_flag",
            |_lua,
             this,
             args: (
                 String,
                 String,
                 Option<String>,
                 Option<String>,
                 Option<String>,
                 Option<bool>,
             )|
             -> mlua::Result<()> {
                this.add_flag(
                    args.0,
                    args.1,
                    args.2,
                    args.3,
                    args.4,
                    false,
                    if let Some(value) = args.5 {
                        EnvironmentValue::Bool(value)
                    } else {
                        EnvironmentValue::None
                    },
                )
            },
        );
        methods.add_method_mut(
            "add_value",
            |_lua,
             this,
             args: (
                 String,
                 String,
                 Option<String>,
                 Option<String>,
                 Option<String>,
                 mlua::Value,
             )|
             -> mlua::Result<()> {
                this.add_value(
                    args.0,
                    args.1,
                    args.2,
                    args.3,
                    args.4,
                    false,
                    EnvironmentValue::from_lua(&args.5)?,
                )
            },
        );
        methods.add_method_mut(
            "add_count",
            |_lua,
             this,
             args: (
                 String,
                 String,
                 Option<String>,
                 Option<String>,
                 Option<String>,
                 mlua::Value,
             )|
             -> mlua::Result<()> {
                this.add_count(
                    args.0,
                    args.1,
                    args.2,
                    args.3,
                    args.4,
                    false,
                    EnvironmentValue::from_lua(&args.5)?,
                )
            },
        );
        methods.add_method_mut(
            "add_list",
            |_lua,
             this,
             args: (
                 String,
                 String,
                 Option<String>,
                 Option<String>,
                 Option<String>,
                 mlua::Value,
             )|
             -> mlua::Result<()> {
                this.add_list(
                    args.0,
                    args.1,
                    args.2,
                    args.3,
                    args.4,
                    false,
                    EnvironmentValue::from_lua(&args.5)?,
                )
            },
        );
        methods.add_method_mut(
            "add_choice",
            |_lua,
             this,
             args: (
                 String,
                 String,
                 Vec<String>,
                 Option<String>,
                 Option<String>,
                 Option<String>,
                 mlua::Value,
             )|
             -> mlua::Result<()> {
                this.add_choice(
                    args.0,
                    args.1,
                    args.3,
                    args.4,
                    args.5,
                    false,
                    args.2,
                    EnvironmentValue::from_lua(&args.6)?,
                )
            },
        );
    }
}
