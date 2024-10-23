use crate::command::{Command, GroupStatus, Targets};
use crate::environment::{Environment, ReadWriteEnvironment, EnvironmentValue};
use crate::error::Result;
use crate::log::Logger;
use crate::node::Node;
use crate::options::{CommandLineParser, Options};
use std::collections::HashMap;
use std::{fmt, fs};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::env;

pub struct Application {
    out_dir: PathBuf,
    options: Environment,
    command_line: Arc<Mutex<CommandLineParser>>,
    init_command: Command,
    command_list: HashMap<String, Vec<String>>,
    verbosity: u32,
    log_why: bool,
    log_colors: Option<bool>,
    generators: Vec<String>,
    files: Vec<Node>,
    thread_count: usize,
    progress_mode: u32,
}

impl Application {
    pub fn init() -> Result<Self> {
        let root_dir = env::current_dir()?
            .file_name()
            .unwrap()
            .to_string_lossy()
            .to_string();
        let mut parser = CommandLineParser::new();
        parser.add_setting("name".to_string(), EnvironmentValue::String(root_dir))?;
        parser.add_setting("author".to_string(), EnvironmentValue::String("".to_string()))?;
        parser.add_setting("version".to_string(), EnvironmentValue::String("0.1.0".to_string()))?;
        parser.add_setting("out".to_string(), EnvironmentValue::Node(Node::from(&PathBuf::from("build/.bolt"))))?;
        let mut paths = vec![EnvironmentValue::Node(Node::from(&env::current_exe()?).parent())];
        if let Some(path_env) = env::var_os("PATH") {
            paths.append(&mut env::split_paths(&path_env).map(|x| EnvironmentValue::Node(Node::from(&x))).collect::<Vec<EnvironmentValue>>());
        }
        parser.add_setting("path".to_string(), EnvironmentValue::Vec(paths))?;
        parser.add_setting("tools_dir".to_string(), EnvironmentValue::Vec(Vec::new()))?;
        parser.add_setting(
            "flavors".to_string(),
            EnvironmentValue::Vec(vec![
                EnvironmentValue::String("debug".to_string()),
                EnvironmentValue::String("final".to_string())
            ]),
        )?;
        parser.add_setting("exe_suffix".to_string(), EnvironmentValue::String(if cfg!(target_os="windows") { ".exe" } else { "" }.to_string()))?;
        parser.add_setting("OS".to_string(), EnvironmentValue::String(env::consts::OS.to_string()))?;

        parser.add_list(
            "commands".to_string(),
            "The command(s) to execute".to_string(),
            EnvironmentValue::Vec(Vec::new()),
        )?
            .set_required();

        parser.add_count(
            "verbose".to_string(),
            "Controls how much information is displayed.\nVerbosity increases with each occurrence of the option.".to_string(),
            EnvironmentValue::Integer(0),
        )?
            .set_category("Options controlling logging")
            .set_short("v");

        parser.add_flag(
            "why".to_string(),
            "Print an explanation for every action.\nFor every command, task generator and task considered, the program will print the reason why it considers it out of date.".to_string(),
            EnvironmentValue::Bool(false),
        )?
            .set_category("Options controlling logging")
            .set_long("why")
            .set_short("w");

        parser.add_flag(
            "color".to_string(),
            "Whether to use colors in the output. Defaults to automatic.".to_string(),
            EnvironmentValue::None,
        )?
            .set_category("Options controlling logging")
            .set_long("color")
            .set_short("c");

        parser.add_list(
            "target".to_string(),
            "Target to be built.\nUse this option multiple times to build several targets.".to_string(),
            EnvironmentValue::None,
        )?
            .set_category("Options controlling task execution")
            .set_long("target")
            .set_short("t");

        parser.add_list(
            "files".to_string(),
            "Files to be built.\nUse this option multiple times to build several files.".to_string(),
            EnvironmentValue::None,
        )?
            .set_category("Options controlling task execution")
            .set_long("file")
            .set_short("f");

        parser.add_value(
            "tidy".to_string(),
            "Keeps build folder tidy.\nFiles in the build folder that do not belong to a task are deleted.".to_string(),
            EnvironmentValue::Bool(true),
        )?
            .set_category("Options controlling task execution")
            .set_long("tidy");

        parser.add_count(
            "progress".to_string(),
            "Controls how progress is reported.\n-p adds a progress bar.\n-pp shows the progress bar and removes the individual task logging.".to_string(),
            EnvironmentValue::Integer(0),
        )?
            .set_category("Options controlling task execution")
            .set_short("p");

        parser.add_value(
            "job_count".to_string(),
            "Controls the maximum number of tasks that can run in parallel. Defaults to the number of processors.".to_string(),
            EnvironmentValue::None,
        )?
            .set_category("Options controlling task execution")
            .set_long("jobs")
            .set_short("j")
            .set_int_type();


        let parser_ptr = Arc::new(Mutex::new(parser));
        let options_context = Options::from_parser(parser_ptr.clone());
        let mut init_command = Command::init()?;
        let mut all_commands = HashMap::from([("init".to_string(), vec!["init".to_string()])]);
        let mut logger = init_command.run(
            options_context.clone(),
            &vec![Arc::new(Mutex::new(ReadWriteEnvironment::new()))],
            &Vec::new(),
            vec!["init".to_string()],
            &mut all_commands,
            Logger::new(None, 0, false),
        )?;

        let parser = parser_ptr.lock().unwrap();
        let options = parser.parse_command_line();

        /* enumerate all saved commands */
        let out_value = options.get_raw("out");
        let out_dir_string = out_value.as_string();
        let out_dir = std::path::Path::new(&out_dir_string);

        let paths = fs::read_dir(out_dir);
        if paths.is_err() {
            if out_dir.is_file() || out_dir.is_symlink() {
                fs::remove_file(out_dir)?;
            }
            fs::create_dir_all(out_dir)?;
        } else {
            let commands_file = PathBuf::from(out_dir).join("cache.json");
            let result = fs::File::open(commands_file);
            if let Ok(file) = result {
                if let Err(err) = init_command.load_from_file(file, &mut all_commands) {
                    logger.error(err.message.as_str());
                }
            }
        }

        let verbosity: u32 = match options.get_raw("verbose") {
            EnvironmentValue::Integer(v) => v as u32,
            _ => 0,
        };
        let log_colors: Option<bool> = match options.get_raw("color") {
            EnvironmentValue::Bool(b) => Some(b),
            _ => None,
        };
        let log_why: bool = match options.get_raw("why") {
            EnvironmentValue::Bool(b) => b,
            _ => false,
        };
        drop(parser);

        let out_value = options.get_raw("out");
        let out_dir_string = out_value.as_string();
        let out_dir = PathBuf::from(&out_dir_string);
        let generators = options.get_raw("target").as_vec();
        let out_node = Node::from(&out_dir);
        let files = options.get_raw("files").as_vec().into_iter().map(|x| out_node.make_node(&PathBuf::from(x))).collect();
        let thread_count = options.get_raw("job_count").as_int();
        let cpu_count = std::thread::available_parallelism()?.get();
        let thread_count = match thread_count {
            n if n > 0 => n as usize,
            n if (-n) as usize >= cpu_count => 1,
            n => cpu_count - (-n as usize)
        };
        let progress_mode = options.get_raw("progress").as_int() as u32;

        Ok(Self {
            out_dir,
            options,
            command_line: parser_ptr,
            init_command,
            command_list: all_commands,
            verbosity,
            log_colors,
            log_why,
            generators,
            files,
            thread_count,
            progress_mode,
        })
    }


    fn run_with_deps<Iter>(
        &mut self,
        mut path: Iter,
        mut logger: Logger,
        run_implicit: bool,
    ) -> Result<Logger>
    where
        Iter: Iterator,
        <Iter as Iterator>::Item: PartialEq<String>,
        <Iter as Iterator>::Item: fmt::Display,
    {
        let mut envs = &Vec::new();
        let mut tools = &Vec::new();
        let mut current_command = &mut self.init_command;
        let mut command_path = Vec::new();

        'run: loop {
            command_path.push(current_command.spec.name.clone());
            let next_item = path.next();
            if !current_command.is_up_to_date() {
                let options = if run_implicit || next_item.is_some() {
                    current_command.get_run_options().map(|options| {
                        let mut options = options.clone();
                        self.command_line
                            .lock()
                            .unwrap()
                            .parse_command_line_into(&mut options);
                        options
                    }).or_else(|| Some(self.options.clone())).unwrap()
                } else {
                    self.options.clone()
                };

                let result = current_command.verify_hash(&options, envs, tools.clone());
                match result {
                    Err(reason) => {
                        logger.why(
                            format!(
                                "command `{}`: running lua scripts because {}",
                                current_command.spec.name,
                                reason
                            ).as_str(),
                        );

                        logger = current_command.run(
                            Options::from_env(options),
                            envs,
                            tools,
                            command_path.clone(),
                            &mut self.command_list,
                            logger,
                        )?;
                    }

                    Ok(_) => {
                        logger.why(format!("command `{}`: lua files are up-to-date", current_command.spec.name).as_str());
                    }
                }

                let mut use_default = true;
                let mut groups = Vec::new();
                for group in &current_command.output.as_ref().unwrap().groups {
                    match &group.1 {
                        GroupStatus::Enabled => groups.push(group.0.clone()),
                        GroupStatus::Conditional(condition) => if self.options.get_raw(condition).as_bool() {
                            use_default = false;
                            groups.push(group.0.clone())
                        },
                        _ => (),
                    }
                }
                if use_default {
                    for group in &current_command.output.as_ref().unwrap().groups {
                        if let GroupStatus::Default = group.1 {
                            groups.push(group.0.clone());
                        }
                    }
                }
                let targets = Targets {
                    groups: &groups,
                    generators: &self.generators,
                    files: &self.files,
                };
                current_command.run_tasks(&self.out_dir, targets, self.thread_count, &mut logger, self.progress_mode)?;
            }

            match next_item {
                None => break,
                Some(cmd_name) => {
                    return if let Some(output) = current_command.output.as_mut() {
                        for command in &mut output.commands {
                            if cmd_name.eq(&command.spec.name) {
                                tools = &output.tools;
                                envs = &output.environments;
                                current_command = command;
                                continue 'run;
                            }
                        }
                        Err(format!("command '{}' not defined", cmd_name).into())
                    } else {
                        Err(format!("command '{}' did not generate any output", current_command.spec.name).into())
                    }
                }
            }
        }

        Ok(logger)
    }

    pub fn run(&mut self) -> Result<()> {
        let mut logger = Logger::new(self.log_colors, self.verbosity, self.log_why);
        let commands = self.options.get_raw("commands").as_vec();

        let commands_file = self.out_dir.join("cache.json");

        for command in commands {
            let command_path: Vec<String>;
            let mut implicit = false;

            if let Some(ref_path) = self.command_list.get(&command) {
                assert!(ref_path[0].eq("init"));
                command_path = ref_path.clone();
            } else if command.as_str()[0..2].eq("re") {
                if let Some(ref_path) = self.command_list.get(&command[2..]) {
                    assert!(ref_path[0].eq("init"));
                    command_path = ref_path.clone();
                    implicit = true;
                } else {
                    return Err(format!("command '{}' not defined", command).into());
                }
            } else {
                return Err(format!("command '{}' not defined", command).into());
            }

            let result = self.run_with_deps(command_path.into_iter().skip(1), logger, implicit);
            let file = fs::File::create(&commands_file)?;
            self.init_command.save_to_file(file)?;

            logger = result?;
        }
        Ok(())
    }
}
