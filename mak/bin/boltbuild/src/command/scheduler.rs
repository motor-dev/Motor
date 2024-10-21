use super::{Command, TaskSeq, CommandStatus, SerializedHash};
use crate::node::Node;
use crate::error::Result;
use crate::log::Logger;
use crate::task::Task;
use crate::driver::Driver;

use std::collections::{HashMap, HashSet};
use std::iter::zip;
use std::mem::swap;
use std::path::{Path, PathBuf};
use std::thread;
use std::time;
use std::time::Duration;
use regex::Regex;
use serde::{Deserialize, Serialize};
use crossbeam::channel::{Sender, Receiver};

impl Command {
    pub(crate) fn run_tasks(
        &mut self,
        out_dir: &Path,
        groups: &[String],
        generators: &[String],
        files: &[Node],
        thread_count: usize,
        logger: &mut Logger,
        progress_mode: u32,
    ) -> Result<()> {
        let output = self.output.as_ref().unwrap();
        if let TaskSeq::List(tasks_pool) = &output.tasks
        {
            let mut scheduler = Scheduler::new(tasks_pool, &output.drivers);

            for (i, task) in tasks_pool.iter().enumerate() {
                if groups.iter().any(|x| x.eq(&task.group)) || generators.iter().any(|x| x.eq(&task.generator)) {
                    scheduler.add_task(i);
                } else {
                    'lookup: for file in files {
                        for output in &task.outputs {
                            if output == file {
                                scheduler.add_task(i);
                                break 'lookup;
                            }
                        }
                    }
                }
            }

            scheduler.load_cache(logger, out_dir, &output.groups);
            let result = scheduler.execute(logger, thread_count, self.spec.name.as_str(), progress_mode);
            scheduler.save_cache(logger, out_dir, &output.groups);

            /* save tasks */
            let safe_file_name = scheduler.invalid_chars.replace_all(self.spec.name.as_str(), "_");
            let task_file = out_dir.join(format!("{}.bin", safe_file_name));
            let mut file = std::fs::File::create(&task_file)?;
            bincode::serde::encode_into_std_write(tasks_pool, &mut file, bincode::config::standard())?;
            //serde_json::to_writer_pretty(file, &tasks)?;
            if let Some(output) = &mut self.output {
                output.tasks = TaskSeq::Cached(task_file);
            }
            self.status = CommandStatus::UpToDate;
            result
        } else {
            self.status = CommandStatus::UpToDate;
            Ok(())
        }
    }
}

enum WorkRequest<'a> {
    FileHash(usize, &'a [&'a PathBuf]),
    Run(usize, blake3::Hash, blake3::Hash),
}

enum WorkResult<'a> {
    FileHashResult(usize, Vec<blake3::Hash>),
    TaskSkipped(usize, Vec<(&'a PathBuf, blake3::Hash)>),
    TaskStart(usize, usize, &'static str),
    TaskResult(usize, usize, i32, String, Vec<(&'a PathBuf, blake3::Hash)>, blake3::Hash, Vec<String>, Vec<PathBuf>, blake3::Hash),
}

#[derive(Serialize, Deserialize, Clone)]
struct TaskCacheEntry {
    environment_dependencies: Vec<String>,
    file_dependencies: Vec<PathBuf>,
    environment_hash: SerializedHash,
    input_hash: SerializedHash,
    dependency_hash: SerializedHash,
}

type BuildCache = HashMap<SerializedHash, TaskCacheEntry>;

struct Scheduler<'command> {
    tasks_pool: &'command Vec<Task>,
    drivers: &'command HashMap<String, Driver>,
    inputs: HashSet<PathBuf>,
    outputs: HashSet<PathBuf>,
    tasks_cache: Vec<Option<TaskCacheEntry>>,
    target_tasks: Vec<usize>,
    invalid_chars: Regex,
}

impl<'command> Scheduler<'command> {
    fn new(tasks_pool: &'command Vec<Task>, drivers: &'command HashMap<String, Driver>) -> Self {
        let mut tasks_cache = Vec::new();
        tasks_cache.resize_with(tasks_pool.len(), || None);
        Self {
            tasks_pool,
            drivers,
            inputs: HashSet::new(),
            outputs: HashSet::new(),
            tasks_cache,
            target_tasks: Vec::new(),
            invalid_chars: Regex::new(r"[<>:/\\|\?\*]+").unwrap(),
        }
    }

    fn add_task(&mut self, index: usize) {
        if !self.target_tasks.iter().any(|&x| x == index) {
            for i in self.tasks_pool[index].predecessors.iter() {
                self.add_task(*i);
            }
            self.target_tasks.push(index);
            for node in &self.tasks_pool[index].inputs {
                self.inputs.insert(node.path().clone());
            }
            for node in &self.tasks_pool[index].outputs {
                self.outputs.insert(node.path().clone());
            }
        }
    }

    fn load_cache<T>(&mut self, logger: &mut Logger, out_dir: &Path, groups: &[(String, T)]) {
        let mut build_cache = BuildCache::new();
        for group in groups {
            let safe_file_name = self.invalid_chars.replace_all(group.0.as_str(), "_");
            let group_cache = out_dir.join(format!("{}.cache", safe_file_name));
            if let Ok(mut file) = std::fs::File::open(&group_cache) {
                match bincode::serde::decode_from_std_read(&mut file, bincode::config::standard()) as std::result::Result<BuildCache, _> {
                    Ok(group_cache) => { build_cache.extend(group_cache); }
                    Err(error) => { logger.warning(format!("Unable to deserialize build cache {:?} ({})", group_cache, error).as_str()); }
                }
            }
        }

        for (task, data) in zip(self.tasks_pool, &mut self.tasks_cache) {
            *data = build_cache.remove(&task.signature);
        }
    }

    fn save_cache<T>(&mut self, logger: &mut Logger, out_dir: &Path, groups: &[(String, T)]) {
        /* save all caches */
        for (group, _) in groups {
            let safe_file_name = self.invalid_chars.replace_all(group.as_str(), "_");
            let mut group_cache = BuildCache::new();
            for (i, task) in self.tasks_pool.iter().enumerate() {
                if task.group.eq(group) {
                    let mut entry = None;
                    swap(&mut entry, &mut self.tasks_cache[i]);
                    if let Some(cache) = entry {
                        group_cache.insert(task.signature.clone(), cache);
                    }
                }
            }
            let cache_filename = out_dir.join(format!("{}.cache", safe_file_name));
            match std::fs::File::create(&cache_filename) {
                Ok(mut file) => {
                    if let Err(e) = bincode::serde::encode_into_std_write(group_cache, &mut file, bincode::config::standard()) {
                        logger.warning(format!("Unable to serialize build cache {:?} ({})", cache_filename, e).as_str());
                    }
                }
                Err(e) => {
                    logger.warning(format!("Unable to serialize build cache {:?} ({})", cache_filename, e).as_str());
                }
            }
            ;
        }
    }

    fn execute_thread(&self, dependency_nodes: &HashSet<&PathBuf>, thread_index: usize, work_pipe: Receiver<WorkRequest>, result_pipe: Sender<WorkResult<'command>>) {
        while let Ok(request) = work_pipe.recv() {
            match request {
                WorkRequest::FileHash(start, path_bufs) => {
                    let mut result = Vec::with_capacity(path_bufs.len());
                    for &path_buf in path_bufs {
                        let mut hasher = blake3::Hasher::new();
                        let file = std::fs::File::open(path_buf).unwrap();
                        let hash = hasher.update_reader(file).unwrap().finalize();
                        result.push(hash);
                    }
                    result_pipe.send(WorkResult::FileHashResult(start, result)).unwrap();
                }
                WorkRequest::Run(task_index, input_hash, dependency_hash) => {
                    let (do_run, reason) = if let Some(cache) = &self.tasks_cache[task_index] {
                        if input_hash != cache.input_hash.0 {
                            (true, "an input file has changed")
                        } else if dependency_hash != cache.dependency_hash.0 {
                            (true, "a dependency file has changed")
                        } else {
                            let mut hasher = blake3::Hasher::new();
                            let env = &self.tasks_pool[task_index].env;
                            let env = env.lock().unwrap();
                            for var in &cache.environment_dependencies {
                                env.get_raw(var.as_str()).hash(&mut hasher);
                            }
                            if !hasher.finalize().eq(&cache.environment_hash.0) {
                                (true, "the environment has been modified")
                            } else {
                                (false, "the task is up-to-date")
                            }
                        }
                    } else {
                        (true, "the task has never been run")
                    };

                    if do_run {
                        result_pipe.send(WorkResult::TaskStart(task_index, thread_index, reason)).unwrap();
                        let task = &self.tasks_pool[task_index];
                        if let Some(driver) = self.drivers.get(&task.name) { driver.execute(); }

                        let dependencies: Vec<PathBuf> = Vec::new();
                        let mut hashes = Vec::new();
                        for output in &self.tasks_pool[task_index].outputs {
                            if dependency_nodes.contains(output.path()) {
                                let hasher = blake3::Hasher::new();
                                hashes.push((output.path(), hasher.finalize()));
                            }
                        }

                        let environment_dependencies: Vec<String> = Vec::new();
                        let mut env_hasher = blake3::Hasher::new();
                        let env = &task.env;
                        let env = env.lock().unwrap();
                        for var in &environment_dependencies {
                            env.get_raw(var.as_str()).hash(&mut env_hasher);
                        }
                        result_pipe.send(WorkResult::TaskResult(
                            task_index,
                            thread_index,
                            0,
                            "".to_string(),
                            hashes,
                            input_hash,
                            environment_dependencies,
                            dependencies,
                            env_hasher.finalize(),
                        )).unwrap();
                    } else {
                        let mut hashes = Vec::new();
                        for output in &self.tasks_pool[task_index].outputs {
                            if dependency_nodes.contains(output.path()) {
                                let hasher = blake3::Hasher::new();
                                hashes.push((output.path(), hasher.finalize()));
                            }
                        }

                        result_pipe.send(WorkResult::TaskSkipped(task_index, hashes)).unwrap();
                    }
                }
            }
        }
    }

    fn execute(
        &mut self,
        logger: &mut Logger,
        thread_count: usize,
        title: &str,
        progress_mode: u32,
    ) -> Result<()> {
        let dependency_nodes = self.inputs.intersection(&self.outputs).collect::<HashSet<_>>();
        let mut thread_activity = ThreadActivity::new(thread_count);

        let mut input_hashes = Vec::new();
        let mut task_work = Vec::new();
        task_work.resize(self.tasks_pool.len(), (usize::MAX, None));

        for &task in &self.target_tasks {
            task_work[task].0 = self.tasks_pool[task].predecessors.len();
        }


        let this = self as &Self;

        thread::scope(|scope| {
            let (send_request, receive_request) = crossbeam::channel::unbounded::<WorkRequest>();
            let (send_result, receive_result) = crossbeam::channel::unbounded::<WorkResult>();
            let timer = time::Instant::now();
            let task_count: usize = self.target_tasks.len();
            let mut processed_tasks: usize = 0;

            let mut file_hashes = HashMap::new();

            for &task in &self.target_tasks {
                for input in &self.tasks_pool[task].inputs {
                    if !dependency_nodes.contains(input.path()) {
                        input_hashes.push(input.path());
                    }
                }
                if let Some(cache) = &self.tasks_cache[task] {
                    for input in &cache.file_dependencies {
                        if !dependency_nodes.contains(input) {
                            input_hashes.push(input);
                        }
                    }
                }
            }

            for thread_index in 0..thread_count {
                /* captured values */
                let send = send_result.clone();
                let receive = receive_request.clone();
                let dependency_nodes = &dependency_nodes;

                scope.spawn(move || this.execute_thread(dependency_nodes, thread_index, receive, send));
            }

            /* post all hashing requests */
            let request_count = thread_count * 3;
            let request_size = input_hashes.len() / request_count;
            let remainder = input_hashes.len() % request_count;
            let mut current = 0_usize;

            for i in 0..request_count {
                let request_size = request_size + (i < remainder) as usize;
                send_request.send(WorkRequest::FileHash(current, &input_hashes[current..current + request_size])).unwrap();
                current += request_size;
            }

            /* wait for all hashing requests to have completed */
            for _ in 0..request_count {
                if let Ok(result) = receive_result.recv() {
                    match result {
                        WorkResult::FileHashResult(start, result) => {
                            for i in 0..result.len() {
                                file_hashes.insert(input_hashes[start + i], result[i]);
                            }
                        }
                        _ => unreachable!()
                    }
                } else {
                    /* todo: error */
                }
            }

            let mut work_index = 0_usize;

            /* Post all tasks that do not have dependencies */
            for &task in &self.target_tasks {
                if task_work[task].0 == 0 {
                    self.on_task_ready(&send_request, task, &file_hashes);
                }
            }

            let task_count_str = task_count.to_string();
            /* wait until all tasks have been executed */
            while processed_tasks != task_count {
                if let Ok(result) = receive_result.recv() {
                    match result {
                        WorkResult::TaskSkipped(task_index, output_hashes) => {
                            work_index += 1;
                            processed_tasks += 1;
                            for (file, hash) in output_hashes {
                                file_hashes.insert(file, hash);
                            }

                            /* copy cache */
                            task_work[task_index].1 = self.tasks_cache[task_index].clone();
                            for &successor in &self.tasks_pool[task_index].successors {
                                task_work[successor].0 -= 1;
                                if task_work[successor].0 == 0 {
                                    self.on_task_ready(&send_request, successor, &file_hashes);
                                }
                            }
                        }
                        WorkResult::TaskStart(task_index, thread_index, reason) => {
                            work_index += 1;
                            thread_activity.switch_on(thread_index);
                            let task = &self.tasks_pool[task_index];
                            logger.why_verbose(format!("Running task {} because {}", task, reason).as_str());
                            let id = if task.inputs.is_empty() {
                                if task.outputs.is_empty() {
                                    task.name.clone()
                                } else {
                                    task.outputs[0].name()
                                }
                            } else {
                                task.inputs[0].name()
                            };
                            log_task_start(logger, work_index, task_count_str.as_str(), format!("{{{}}} {}/{}", task.name, task.group, id).as_str());
                        }
                        WorkResult::TaskResult(
                            task_index,
                            thread_index,
                            result,
                            log,
                            output_hashes,
                            input_hash,
                            environment_dependencies,
                            file_dependencies,
                            environment_hash
                        ) => {
                            for (file, hash) in output_hashes {
                                file_hashes.insert(file, hash);
                            }
                            processed_tasks += 1;
                            thread_activity.switch_off(thread_index);
                            let task = &self.tasks_pool[task_index];
                            log_task_end(logger, result, task.inputs[0].path(), log.as_str());
                            for &successor in &task.successors {
                                task_work[successor].0 -= 1;
                                if task_work[successor].0 == 0 {
                                    self.on_task_ready(&send_request, successor, &file_hashes);
                                }
                            }
                            let hasher = blake3::Hasher::new();
                            task_work[task_index].1 = Some(TaskCacheEntry {
                                environment_dependencies,
                                file_dependencies,
                                environment_hash: SerializedHash(environment_hash),
                                input_hash: SerializedHash(input_hash),
                                dependency_hash: SerializedHash(hasher.finalize()),
                            });
                        }
                        _ => unreachable!()
                    }
                } else {
                    /* todo: error */
                }
                if progress_mode >= 1 {
                    log_progress(logger, title, thread_activity.get_graph(), processed_tasks, task_count, timer.elapsed());
                }
            }
        });

        for &task in &self.target_tasks {
            if let Some(cache) = &task_work[task].1 {
                self.tasks_cache[task] = Some(cache.clone());
            }
        }

        logger.clear_status();
        Ok(())
    }

    fn on_task_ready(&self, work_pipe: &Sender<WorkRequest>, task_index: usize, file_hashes: &HashMap<&PathBuf, blake3::Hash>) {
        let task = &self.tasks_pool[task_index];
        let mut input_hasher = blake3::Hasher::new();
        for input in &task.inputs {
            input_hasher.update(file_hashes.get(input.path()).unwrap().as_bytes());
        }

        let mut dependency_hasher = blake3::Hasher::new();
        if let Some(cache) = &self.tasks_cache[task_index] {
            for input in &cache.file_dependencies {
                dependency_hasher.update(file_hashes.get(input).unwrap().as_bytes());
            }
        }

        work_pipe.send(WorkRequest::Run(task_index, input_hasher.finalize(), dependency_hasher.finalize())).unwrap();
    }
}

struct ThreadActivity {
    thread_count: usize,
    thread_activity: Vec<usize>,
    thread_activity_graph: Vec<char>,
}

impl ThreadActivity {
    const GRAPH_HALF: [char; 4] = [' ', '▄', '▀', '█'];
    const GRAPH_QUARTERS: [char; 16] = [
        ' ', '▖', '▘', '▌',
        '▗', '▄', '▚', '▙',
        '▝', '▞', '▀', '▛',
        '▐', '▟', '▜', '█'];
    fn new(thread_count: usize) -> Self {
        Self {
            thread_count,
            thread_activity: vec![0; (thread_count + 3) / 4],
            thread_activity_graph: vec![' '; (thread_count + 3) / 4],
        }
    }

    fn switch_on(&mut self, index: usize) {
        let cell = index / 4;
        let index = index % 4;
        self.thread_activity[cell] |= 1 << index;

        match self.thread_count {
            1 => { self.thread_activity_graph[0] = '█' }
            2 => { self.thread_activity_graph[cell] = Self::GRAPH_HALF[self.thread_activity[cell]] }
            _ => { self.thread_activity_graph[cell] = Self::GRAPH_QUARTERS[self.thread_activity[cell]] }
        }
    }

    fn switch_off(&mut self, index: usize) {
        let cell = index / 4;
        let index = index % 4;
        self.thread_activity[cell] &= !(1 << index);

        match self.thread_count {
            1 => { self.thread_activity_graph[0] = ' ' }
            2 => { self.thread_activity_graph[cell] = Self::GRAPH_HALF[self.thread_activity[cell]] }
            _ => { self.thread_activity_graph[cell] = Self::GRAPH_QUARTERS[self.thread_activity[cell]] }
        }
    }

    fn get_graph(&self) -> &[char] {
        self.thread_activity_graph.as_slice()
    }
}

fn log_task_start(logger: &mut Logger, index: usize, task_count: &str, message: &str) {
    logger.print(format!("[{:width$}/{}] {}", index, task_count, message, width = task_count.len()).as_str());
}

fn log_task_end(logger: &mut Logger, result: i32, input: &PathBuf, message: &str) {
    if result != 0 {
        logger.error(format!("{:?}:\n{}", input, message).as_str());
    } else if !message.is_empty() {
        logger.print(format!("{:?};\n{}", input, message).as_str());
    }
}

const GRAPH_EIGTHS: [char; 7] = [
    '▏', '▎', '▍', '▌', '▋', '▊', '▉'];

fn log_progress(logger: &mut Logger, title: &str, thread_activity: &[char], finished_tasks: usize, task_count: usize, elapsed: Duration) {
    let (f1, unit, f2) = if elapsed.as_secs() > 60 {
        if elapsed.as_secs() > 60 * 60 {
            /* hour:minutes */
            (3600 * 1000, 'h', 60 * 1000)
        } else {
            /* minutes:seconds */
            (60 * 1000, 'm', 1000)
        }
    } else {
        /* seconds:centiseconds */
        (1000, 's', 10)
    };
    let v1 = elapsed.as_millis() / f1;
    let v2 = (elapsed.as_millis() - f1 * v1) / f2;

    let terminal_width = logger.terminal_width();
    let progress_width = terminal_width - 9 - thread_activity.len();
    let progress_bar = if title.len() > progress_width {
        let mut title = title[..progress_width - 3].to_string();
        title.push('.');
        title.push('.');
        title.push('.');
        title
    } else {
        let mut title = title.to_string();
        while title.len() < progress_width {
            title.push(' ');
        }
        title
    };

    let progress = (finished_tasks * progress_width * 8) / task_count;
    let remainder = progress % 8;
    let progress = progress / 8;

    if remainder == 0 {
        logger.set_status(format!(
            "{{bg:green}}{{black}}{}{{green}}{{bg:black}}{}{{reset}}{{bg:reset}}[{{red}}{}{{reset}}][{{green}}{:2}{}{:02}{{reset}}]",
            &progress_bar[0..progress],
            &progress_bar[progress..progress_bar.len()],
            thread_activity.iter().collect::<String>(),
            v1, unit, v2).as_str());
    } else {
        logger.set_status(format!(
            "{{bg:green}}{{black}}{}{{green}}{{bg:black}}{}{}{{reset}}{{bg:reset}}[{{red}}{}{{reset}}][{{green}}{:2}{}{:02}{{reset}}]",
            &progress_bar[0..progress],
            GRAPH_EIGTHS[remainder - 1],
            &progress_bar[progress + 1..progress_bar.len()],
            thread_activity.iter().collect::<String>(),
            v1, unit, v2).as_str());
    }
}