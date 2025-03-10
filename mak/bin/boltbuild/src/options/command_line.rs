use super::CommandLineParser;
use crate::environment::{FlatMap, MapValue};
use clap::ArgAction;

pub(crate) struct Interface {
    long: Option<String>,
    short: Option<String>,
    category: Option<String>,
    help: String,
    required: bool,
    choice_list: Option<Vec<String>>,
    action: ArgAction,
    int_type: bool,
}

pub(super) struct Argument {
    pub(super) name: String,
    pub(super) interface: Option<Interface>,
}

impl Interface {
    pub(crate) fn set_long(&mut self, long: impl ToString) -> &mut Self {
        self.long = Some(long.to_string());
        self
    }
    pub(crate) fn set_short(&mut self, short: impl ToString) -> &mut Self {
        self.short = Some(short.to_string());
        self
    }
    pub(crate) fn set_category(&mut self, category: impl ToString) -> &mut Self {
        self.category = Some(category.to_string());
        self
    }
    pub(crate) fn set_required(&mut self) -> &mut Self {
        self.required = true;
        self
    }
    pub(crate) fn set_choice(&mut self, choice_list: &[impl ToString]) -> &mut Self {
        self.choice_list = Some(choice_list.iter().map(|x| x.to_string()).collect());
        self
    }
    pub(crate) fn set_int_type(&mut self) -> &mut Self {
        self.int_type = true;
        self
    }
}

impl CommandLineParser {
    pub(crate) fn new() -> Self {
        Self {
            options: Vec::new(),
            map: FlatMap::new(),
        }
    }

    pub(crate) fn add_setting(&mut self, name: String, default: MapValue) -> mlua::Result<()> {
        if self.options.iter().any(|x| x.name.eq(&name)) {
            Err(mlua::Error::RuntimeError(
                format!(
                    "'{}': an option is already registered with this name",
                    &name
                )
                .to_string(),
            ))
        } else {
            self.map.set(&name, default);
            self.options.push(Argument {
                name,
                interface: None,
            });
            Ok(())
        }
    }

    fn add_option(
        &mut self,
        name: String,
        help: String,
        default: MapValue,
        action: ArgAction,
    ) -> mlua::Result<&mut Interface> {
        if self.options.iter().any(|x| x.name.eq(&name)) {
            Err(mlua::Error::RuntimeError(
                format!(
                    "'{}': an option is already registered with this name",
                    &name
                )
                .to_string(),
            ))
        } else {
            self.map.set(&name, default);
            self.options.push(Argument {
                name,
                interface: Some(Interface {
                    long: None,
                    short: None,
                    category: None,
                    help,
                    required: false,
                    choice_list: None,
                    action,
                    int_type: false,
                }),
            });
            Ok(self.options.last_mut().unwrap().interface.as_mut().unwrap())
        }
    }

    pub(crate) fn add_flag(
        &mut self,
        name: String,
        help: String,
        default: MapValue,
    ) -> mlua::Result<&mut Interface> {
        self.add_option(name, help, default, ArgAction::SetTrue)
    }

    pub(crate) fn add_value(
        &mut self,
        name: String,
        help: String,
        default: MapValue,
    ) -> mlua::Result<&mut Interface> {
        self.add_option(name, help, default, ArgAction::Set)
    }

    pub(crate) fn add_count(
        &mut self,
        name: String,
        help: String,
        default: MapValue,
    ) -> mlua::Result<&mut Interface> {
        self.add_option(name, help, default, ArgAction::Count)
    }

    pub(crate) fn add_choice(
        &mut self,
        name: String,
        help: String,
        choice_list: &[String],
        default: MapValue,
    ) -> mlua::Result<&mut Interface> {
        Ok(self
            .add_option(name, help, default, ArgAction::Set)?
            .set_choice(choice_list))
    }

    pub(crate) fn add_list(
        &mut self,
        name: String,
        help: String,
        default: MapValue,
    ) -> mlua::Result<&mut Interface> {
        self.add_option(name, help, default, ArgAction::Append)
    }

    pub(crate) fn parse_command_line(&self) -> FlatMap {
        let mut result = self.map.clone();
        self.parse_command_line_into(&mut result);
        result
    }

    pub(crate) fn parse_command_line_into(&self, env: &mut FlatMap) {
        use clap::{
            builder::PossibleValue, builder::PossibleValuesParser, parser::ValueSource, Arg,
            Command,
        };
        let mut cmd = Command::new("boltbuild");
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
                if interface.int_type {
                    arg = arg.value_parser(clap::value_parser!(i64));
                }
                if let Some(choice) = &interface.choice_list {
                    arg = arg.value_parser(PossibleValuesParser::new(
                        choice
                            .iter()
                            .map(PossibleValue::new)
                            .collect::<Vec<PossibleValue>>(),
                    ));
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
                    if let Some(source) = matches.value_source(option.name.as_str()) {
                        if source != ValueSource::DefaultValue {
                            match interface.action {
                                ArgAction::SetTrue => env.set(
                                    option.name.as_str(),
                                    MapValue::Bool(matches.get_flag(option.name.as_str())),
                                ),
                                ArgAction::Set => {
                                    if interface.int_type {
                                        env.set(
                                            option.name.as_str(),
                                            MapValue::Integer(
                                                *matches
                                                    .get_one::<i64>(option.name.as_str())
                                                    .unwrap(),
                                            ),
                                        )
                                    } else {
                                        env.set(
                                            option.name.as_str(),
                                            MapValue::String(
                                                matches
                                                    .get_one::<String>(option.name.as_str())
                                                    .unwrap()
                                                    .to_string(),
                                            ),
                                        )
                                    }
                                }
                                ArgAction::Count => env.set(
                                    option.name.as_str(),
                                    MapValue::Integer(
                                        matches.get_count(option.name.as_str()).into(),
                                    ),
                                ),
                                ArgAction::Append => {
                                    let mut vec = Vec::<MapValue>::new();
                                    for m in
                                        matches.get_many::<String>(option.name.as_str()).unwrap()
                                    {
                                        vec.push(MapValue::String(m.clone()));
                                    }
                                    env.set(option.name.as_str(), MapValue::Vec(vec))
                                }
                                _ => panic!("unknown option type"),
                            }
                        }
                    }
                }
            }
        }
    }
}
