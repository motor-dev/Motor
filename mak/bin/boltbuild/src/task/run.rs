use super::{Task, SPLIT_RE, ENV_RE};

use regex::Captures;
use subprocess::ExitStatus;

impl Task {
    pub(crate) fn run_command(&self, command: &str, extra_args: Vec<String>) -> (String, String, u32) {
        let mut command_line = Vec::new();

        for argument in SPLIT_RE.split(command) {
            if let Some(captures) = ENV_RE.captures(argument) {
                match self.expand(argument, captures) {
                    Ok(value) => command_line.extend(value),
                    Err(message) => return (command.to_string(), message, 1),
                }
            }
        }
        command_line.extend(extra_args);

        let command = command_line.join(" ");

        match subprocess::Popen::create(
            &command_line,
            subprocess::PopenConfig {
                stdin: subprocess::Redirection::None,
                stdout: subprocess::Redirection::Pipe,
                stderr: subprocess::Redirection::Merge,
                ..subprocess::PopenConfig::default()
            },
        ) {
            Ok(mut subprocess) => {
                match subprocess.communicate(None) {
                    Ok(result) => {
                        match subprocess.wait() {
                            Ok(status) => {
                                match status {
                                    ExitStatus::Exited(return_code) => (command, result.0.unwrap(), return_code),
                                    _ => (command, result.0.unwrap(), 1),
                                }
                            }
                            Err(error) => {
                                (command, error.to_string(), 1)
                            }
                        }
                    }
                    Err(error) => {
                        (command, error.to_string(), 1)
                    }
                }
            }
            Err(error) => (command, error.to_string(), 1),
        }
    }

    fn expand(&self, argument: &str, capture: Captures) -> Result<Vec<String>, String> {
        let mut env = self.env.lock().unwrap();
        let var = capture.get(2).unwrap();
        let var_name = var.as_str();
        let value = env.get(var_name);
        let start = capture.get(0).unwrap().start();
        let end = capture.get(0).unwrap().end();
        if value.is_none() {
            if start != 0 || end != argument.len() {
                let mut result = argument[0..start].to_string();
                result.push_str(&argument[end..argument.len()]);
                Ok(vec![result])
            } else {
                Ok(Vec::new())
            }
        } else {
            let mut result = value.as_vec();
            if let Some(index) = capture.get(4) {
                let index = index.as_str().parse::<usize>().unwrap();
                if index >= result.len() {
                    return Err(format!("requesting {}[{}] but the list has {} elements.", var_name, index, result.len()));
                }
                result = vec![result[index].clone()];
            }

            if !result.is_empty() {
                if let Some(pattern) = capture.get(1) {
                    let var_name = &pattern.as_str()[0..pattern.len() - 1];
                    let pattern = env.get(var_name);
                    if pattern.is_list() {
                        let mut flattened_list = Vec::new();
                        let pattern = pattern.as_vec();
                        for a in result {
                            if start != 0 {
                                flattened_list.push(argument[0..start].to_string());
                            }

                            flattened_list.extend(pattern.clone());
                            flattened_list.push(a);

                            if end != argument.len() {
                                flattened_list.push(argument[0..start].to_string());
                            }
                        }
                        result = flattened_list;
                    } else {
                        let pattern = pattern.as_string();
                        if !pattern.contains("%s") {
                            for a in &mut result {
                                *a = format!("{}{}{}{}", &argument[0..start], pattern, a, &argument[end..argument.len()]);
                            }
                        } else {
                            for a in &mut result {
                                *a = format!("{}{}{}", &argument[0..start], pattern.replace("%s", a), &argument[end..argument.len()]);
                            }
                        }
                    }
                } else {
                    for a in &mut result {
                        *a = format!("{}{}{}", &argument[0..start], a, &argument[end..argument.len()]);
                    }
                }
                Ok(result)
            } else if start != 0 || end != argument.len() {
                let mut result = argument[0..start].to_string();
                result.push_str(&argument[end..argument.len()]);
                Ok(vec![result])
            } else {
                Ok(Vec::new())
            }
        }
    }
}

