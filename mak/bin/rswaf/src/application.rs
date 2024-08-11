use crate::command::Command;
use crate::environment::{Environment, EnvironmentValue};
use crate::error::Result;
use crate::log::Logger;
use crate::node::Node;
use crate::options::{CommandLineParser, Options};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::env;

pub struct Application {
    options: Arc<Mutex<Environment>>,
    command_line: Arc<Mutex<CommandLineParser>>,
    init_command: Command,
    command_list: HashMap<String, Vec<String>>,
    verbosity: u32,
    log_why: bool,
    log_colors: Option<bool>,
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
        parser.add_setting(
            "author".to_string(),
            EnvironmentValue::String("".to_string()),
        )?;
        parser.add_setting(
            "version".to_string(),
            EnvironmentValue::String("0.1.0".to_string()),
        )?;
        parser.add_setting(
            "out".to_string(),
            EnvironmentValue::Node(Node::from(&PathBuf::from("build/.rswaf"))),
        )?;
        let mut paths = vec![EnvironmentValue::Node(Node::from(&PathBuf::from(env::current_exe()?)).parent())];
        if let Some(path_env) = env::var_os("PATH") {
            paths.append(&mut env::split_paths(&path_env).map(|x| EnvironmentValue::Node(Node::from(&x))).collect::<Vec<EnvironmentValue>>());
        }
        parser.add_setting(
            "path".to_string(),
            EnvironmentValue::Vec(paths),
        )?;
        parser.add_setting(
            "flavors".to_string(),
            EnvironmentValue::Vec(vec![EnvironmentValue::String("debug".to_string()), EnvironmentValue::String("final".to_string())]),
        )?;
        parser.add_setting(
            "exe_suffix".to_string(),
            EnvironmentValue::String(if cfg!(target_os="windows") { ".exe" } else { "" }.to_string()),
        )?;
        parser.add_setting(
            "OS".to_string(),
            EnvironmentValue::String(env::consts::OS.to_string()),
        )?;
        parser.add_list(
            "commands".to_string(),
            "The command(s) to execute".to_string(),
            None,
            None,
            None,
            true,
            EnvironmentValue::Vec(Vec::new()),
        )?;
        parser.add_count(
            "verbose".to_string(),
            "Controls how much information is displayed.\nVerbosity increases with each occurrence of the option.".to_string(),
            Some("Options controlling logging".to_string()),
            None,
            Some("v".to_string()),
            false,
            EnvironmentValue::Integer(0),
        )?;
        parser.add_flag(
            "why".to_string(),
            "Print an explanation for every action.\nFor every command, task generator and task considered, the program will print the reason why it considers it out of date.".to_string(),
            Some("Options controlling logging".to_string()),
            Some("why".to_string()),
            Some("w".to_string()),
            false,
            EnvironmentValue::Bool(false),
        )?;
        parser.add_flag(
            "color".to_string(),
            "Whether to use colors in the output. Defaults to automatic.".to_string(),
            Some("Options controlling logging".to_string()),
            Some("color".to_string()),
            Some("c".to_string()),
            false,
            EnvironmentValue::None,
        )?;
        parser.add_list(
            "target".to_string(),
            "Target to be built.\nUse this option multiple times to build several targets.".to_string(),
            Some("Options controlling task execution".to_string()),
            Some("target".to_string()),
            Some("t".to_string()),
            false,
            EnvironmentValue::None,
        )?;
        parser.add_value(
            "tidy".to_string(),
            "Keeps build folder tidy.\nFiles in the build folder that do not belong to a task are deleted.".to_string(),
            Some("Options controlling task execution".to_string()),
            Some("tidy".to_string()),
            None,
            false,
            EnvironmentValue::Bool(true),
        )?;
        parser.add_count(
            "progress".to_string(),
            "Controls how progress is reported.\n-p adds a progress bar.\n-pp shows the progress bar and removes the individual task logging.".to_string(),
            Some("Options controlling task execution".to_string()),
            None,
            Some("p".to_string()),
            false,
            EnvironmentValue::Integer(0),
        )?;
        parser.add_value(
            "job_count".to_string(),
            "Controls the maximum number of tasks that can run in parallel. Defaults to the number of processors.".to_string(),
            Some("Options controlling task execution".to_string()),
            Some("jobs".to_string()),
            Some("j".to_string()),
            false,
            EnvironmentValue::None,
        )?;
        let parser_ptr = Arc::new(Mutex::new(parser));
        let options_context = Options::from_parser(parser_ptr.clone());
        let mut init_command = Command::init()?;
        let mut all_commands = HashMap::from([("init".to_string(), vec!["init".to_string()])]);
        let mut logger = init_command.run(
            options_context.clone(),
            &vec![Arc::new(Mutex::new(Environment::new()))],
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
                fs::remove_file(&out_dir)?;
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

        Ok(Self {
            options: Arc::new(Mutex::new(options)),
            command_line: parser_ptr,
            init_command,
            command_list: all_commands,
            verbosity,
            log_colors,
            log_why,
        })
    }

    pub fn run(&mut self) -> Result<()> {
        let mut logger = Logger::new(self.log_colors, self.verbosity, self.log_why);
        let commands = self.options.lock().unwrap().get_raw("commands").as_vec();
        let out_value = self.options.lock().unwrap().get_raw("out");
        let out_dir_string = out_value.as_string();
        let out_dir = std::path::Path::new(&out_dir_string);
        let commands_file = PathBuf::from(out_dir).join("cache.json");

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

            logger = self.init_command.run_with_deps(
                command_path.into_iter().skip(1),
                &Vec::new(),
                self.options.clone(),
                self.command_line.clone(),
                Vec::new(),
                &mut self.command_list,
                logger,
                implicit,
            )?;
            let result = fs::File::create(&commands_file)?;
            self.init_command.save_to_file(result)?;
        }
        Ok(())
    }
}
