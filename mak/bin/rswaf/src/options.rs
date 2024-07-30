use crate::environment::{Environment, EnvironmentValue};
use clap::ArgAction;
use mlua::{MetaMethod, UserData, UserDataMethods};
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
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        help: String,
        required: bool,
        default: EnvironmentValue,
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
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        help: String,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            category,
            long,
            short,
            help,
            required,
            default,
            ArgAction::SetTrue,
        )
    }

    pub(crate) fn add_value(
        self: &mut Self,
        name: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        help: String,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            category,
            long,
            short,
            help,
            required,
            default,
            ArgAction::Set,
        )
    }

    pub(crate) fn add_count(
        self: &mut Self,
        name: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        help: String,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            category,
            long,
            short,
            help,
            required,
            default,
            ArgAction::Count,
        )
    }

    pub(crate) fn add_list(
        self: &mut Self,
        name: String,
        category: Option<String>,
        long: Option<String>,
        short: Option<String>,
        help: String,
        required: bool,
        default: EnvironmentValue,
    ) -> mlua::Result<()> {
        self.add_option(
            name,
            category,
            long,
            short,
            help,
            required,
            default,
            ArgAction::Append,
        )
    }

    pub(crate) fn parse_command_line(self: &Self) -> Environment {
        // clap insists all arguments should be &'static str even though the parser only exists here.
        // this means leaking all command line options.
        let mut env = Environment::new();
        for option in &self.options {
            env.set(option.name.as_str(), option.default.clone());
        }
        self.parse_command_line_into(&mut env);
        env
    }

    pub(crate) fn parse_command_line_into(self: &Self, env: &mut Environment) {
        use clap::{Arg, Command};
        let mut cmd = Command::new("rswaf");
        for option in &self.options {
            if let Some(interface) = &option.interface {
                let mut arg = Arg::new(Box::leak(option.name.clone().into_boxed_str()).trim());
                if let Some(category) = &interface.category {
                    arg = arg.help_heading(Box::leak(category.clone().into_boxed_str()).trim());
                }
                if let Some(long) = &interface.long {
                    arg = arg.long(Box::leak(long.clone().into_boxed_str()).trim());
                }
                if let Some(short) = &interface.short {
                    arg = arg.short(short.as_str().trim().chars().next().unwrap());
                }
                arg = arg.help(Box::leak(interface.help.clone().into_boxed_str()).trim());
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
        methods.add_method_mut(
            "add_option",
            |_lua,
             this,
             args: (
                String,
                Option<String>,
                Option<String>,
                Option<String>,
                String,
                mlua::Value,
            )|
             -> mlua::Result<()> {
                this.add_flag(
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
            "add_value",
            |_lua,
             this,
             args: (
                String,
                Option<String>,
                Option<String>,
                Option<String>,
                String,
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
                Option<String>,
                Option<String>,
                Option<String>,
                String,
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
    }
}
