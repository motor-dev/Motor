use super::{Command, CommandStatus, SerializedHash, Targets, TaskSeq};
use crate::driver::Driver;
use crate::environment::Hash;
use crate::error::Result;
use crate::log::Logger;
use crate::node::Node;
use crate::task::Task;
use crossbeam::channel::{Receiver, Sender};
use serde::{Deserialize, Serialize};
use std::cmp::max;
use std::collections::hash_map::Entry;
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::iter::zip;
use std::mem::swap;
use std::path::Path;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time;
use std::time::Duration;

impl Command {
    pub(crate) fn run_tasks(
        &mut self,
        out_dir: &Path,
        targets: Targets,
        thread_count: usize,
        logger: &mut Logger,
        progress_mode: u32,
    ) -> Result<()> {
        let output = self.output.as_ref().unwrap();
        if let TaskSeq::List(tasks_pool) = &output.tasks {
            let (mut tasks_cache, cache) = load_cache(tasks_pool, logger, out_dir, &output.groups);

            let mut scheduler = Scheduler::new(tasks_pool, &output.drivers);
            let mut inputs = HashSet::new();
            let mut outputs = HashSet::new();
            for (i, task) in tasks_pool.iter().enumerate() {
                if targets.groups.iter().any(|x| x.eq(&task.group))
                    || targets.generators.iter().any(|x| x.eq(&task.generator))
                {
                    scheduler.add_task(i, &tasks_cache, &mut inputs, &mut outputs);
                } else {
                    'lookup: for file in targets.files {
                        for output in &task.outputs {
                            if output == file {
                                scheduler.add_task(i, &tasks_cache, &mut inputs, &mut outputs);
                                break 'lookup;
                            }
                        }
                    }
                }
            }

            let mut dependency_nodes = outputs
                .iter()
                .filter(|x| inputs.contains(x))
                .cloned()
                .collect::<HashSet<_>>();

            for input in inputs {
                let mut maybe_parent = input.parent();
                while let Some(parent) = maybe_parent {
                    if outputs.contains(&parent) {
                        dependency_nodes.insert(parent);
                        break;
                    }
                    maybe_parent = parent.parent();
                }
            }

            let (result, new_cache) = scheduler.execute(
                dependency_nodes,
                &tasks_cache,
                logger,
                thread_count,
                self.spec.name.as_str(),
                progress_mode,
            );

            let mut tidy = HashSet::new();
            for (index, value) in new_cache.into_iter().enumerate() {
                if let Some(cache) = value {
                    outputs.extend(cache.all_output.iter().cloned());
                    if let Some(old_cache) = &tasks_cache[index] {
                        tidy.extend(old_cache.all_output.iter().cloned());
                    }
                    tasks_cache[index] = Some(cache);
                }
            }

            for group_cache in cache {
                for (_, cache) in group_cache {
                    tidy.extend(cache.all_output);
                }
            }

            save_cache(
                tasks_pool,
                logger,
                out_dir,
                &output.groups,
                &mut tasks_cache,
            );

            for file in tidy {
                if !outputs.contains(&file) && !file.is_dir() {
                    if progress_mode < 2 {
                        logger.colored_println(format!("{{dim}}[rm] {{reset}}{}", file).as_str());
                    }
                    std::fs::remove_file(file.path())?;

                    let mut maybe_parent = file.parent();
                    while let Some(parent) = maybe_parent {
                        if parent.is_dir() && parent.path().read_dir()?.next().is_none() {
                            if progress_mode < 2 {
                                logger.colored_println(
                                    format!("{{dim}}[rm] {{reset}}{}", parent).as_str(),
                                );
                            }
                            std::fs::remove_dir(parent.path())?;
                            maybe_parent = parent.parent();
                        } else {
                            break;
                        }
                    }
                }
            }

            /* save tasks */
            let task_file = out_dir.join(format!("{}.bin", self.spec.fs_name));
            let mut file = File::create(&task_file)?;
            bincode::serde::encode_into_std_write(
                tasks_pool,
                &mut file,
                bincode::config::standard(),
            )?;
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
    FileHash(usize, &'a [Node]),
    Run(usize, blake3::Hash, blake3::Hash),
}

struct DependencyRequest {
    file_dependencies: Vec<Node>,
    input_hash: blake3::Hash,
    environment_dependencies: Vec<String>,
    environment_hash: blake3::Hash,
    driver_dependencies: Vec<Node>,
    driver_hash: SerializedHash,
    extra_output: Vec<Node>,
}

struct TaskResult {
    task_index: usize,
    thread_index: usize,
    exit_code: u32,
    command: String,
    log: String,
    output_hashes: Vec<(Node, blake3::Hash)>,
}

enum WorkResult<'a> {
    FileHashResult(usize, Vec<blake3::Hash>),
    TaskSkipped(usize, Vec<(Node, blake3::Hash)>),
    TaskStart(usize, usize, String, &'a str),
    TaskResult(TaskResult),
    DependencyResult(usize, TaskCacheEntry),
    TaskCanceled(usize),
    Panic(),
}

#[derive(Serialize, Deserialize, Clone)]
struct TaskCacheEntry {
    environment_dependencies: Vec<String>,
    file_dependencies: Vec<Node>,
    driver_dependencies: Vec<Node>,
    environment_hash: SerializedHash,
    input_hash: SerializedHash,
    dependency_hash: SerializedHash,
    driver_hash: SerializedHash,
    all_output: Vec<Node>,
}

type BuildCache = HashMap<SerializedHash, TaskCacheEntry>;

struct Scheduler<'command> {
    tasks_pool: &'command Vec<Task>,
    drivers: &'command HashMap<String, Driver>,
    target_tasks: Vec<usize>,
    abort: AtomicBool,
}

impl<'command> Scheduler<'command> {
    fn new(tasks_pool: &'command Vec<Task>, drivers: &'command HashMap<String, Driver>) -> Self {
        Self {
            tasks_pool,
            drivers,
            target_tasks: Vec::new(),
            abort: AtomicBool::new(false),
        }
    }

    fn add_task(
        &mut self,
        index: usize,
        tasks_cache: &'command Vec<Option<TaskCacheEntry>>,
        inputs: &mut HashSet<&'command Node>,
        outputs: &mut HashSet<Node>,
    ) {
        if !self.target_tasks.iter().any(|&x| x == index) {
            for i in self.tasks_pool[index].predecessors.iter() {
                self.add_task(*i, tasks_cache, inputs, outputs);
            }
            self.target_tasks.push(index);
            for node in &self.tasks_pool[index].inputs {
                inputs.insert(node);
            }
            for node in &self.tasks_pool[index].outputs {
                outputs.insert(node.clone());
            }
            if let Some(cache) = &tasks_cache[index] {
                for node in &cache.all_output {
                    outputs.insert(node.clone());
                }
                for path in &cache.file_dependencies {
                    inputs.insert(path);
                }
            }
        }
    }

    fn execute_dependency_thread(
        &self,
        work_pipe: Receiver<(usize, DependencyRequest)>,
        result_pipe: Sender<WorkResult<'command>>,
    ) {
        let mut dependency_hashes = HashMap::new();
        while let Ok((task_index, mut request)) = work_pipe.recv() {
            let mut hasher = blake3::Hasher::new();
            for dependency in &request.file_dependencies {
                match dependency_hashes.entry(dependency.clone()) {
                    Entry::Vacant(entry) => {
                        let mut dep_hasher = blake3::Hasher::new();
                        let file = File::open(dependency.path()).unwrap();
                        dep_hasher.update_reader(file).unwrap();
                        let hash = dep_hasher.finalize();
                        hasher.update(hash.as_bytes());
                        entry.insert(hash);
                    }
                    Entry::Occupied(entry) => {
                        hasher.update(entry.get().as_bytes());
                    }
                }
            }
            request
                .extra_output
                .extend(self.tasks_pool[task_index].outputs.iter().cloned());
            result_pipe
                .send(WorkResult::DependencyResult(
                    task_index,
                    TaskCacheEntry {
                        environment_dependencies: request.environment_dependencies,
                        file_dependencies: request.file_dependencies,
                        environment_hash: SerializedHash(request.environment_hash),
                        input_hash: SerializedHash(request.input_hash),
                        dependency_hash: SerializedHash(hasher.finalize()),
                        driver_dependencies: request.driver_dependencies,
                        driver_hash: request.driver_hash,
                        all_output: request.extra_output,
                    },
                ))
                .unwrap();
        }
    }

    fn execute_thread(
        &self,
        dependency_nodes: &HashSet<Node>,
        tasks_cache: &[Option<TaskCacheEntry>],
        thread_index: usize,
        work_pipe: Receiver<WorkRequest>,
        result_pipe: Sender<WorkResult<'command>>,
        dependency_pipe: Sender<(usize, DependencyRequest)>,
    ) {
        while let Ok(request) = work_pipe.recv() {
            match request {
                WorkRequest::FileHash(start, paths) => {
                    let mut result = Vec::with_capacity(paths.len());
                    for path in paths {
                        let mut hasher = blake3::Hasher::new();
                        let file = File::open(path.path());
                        if let Ok(file) = file {
                            hasher.update_reader(file).unwrap();
                        }
                        let hash = hasher.finalize();
                        result.push(hash);
                    }
                    result_pipe
                        .send(WorkResult::FileHashResult(start, result))
                        .unwrap();
                }
                WorkRequest::Run(task_index, input_hash, dependency_hash) => {
                    if self.abort.load(Ordering::Acquire) {
                        result_pipe
                            .send(WorkResult::TaskCanceled(task_index))
                            .unwrap();
                    } else {
                        let task = &self.tasks_pool[task_index];
                        let driver = self.drivers.get(&task.driver).unwrap();
                        let mut hashes = Vec::new();
                        let (do_run, reason) = match &tasks_cache[task_index] {
                            Some(cache) if input_hash != cache.input_hash.0 => {
                                (true, "an input file has changed".to_string())
                            }
                            Some(cache) if dependency_hash != cache.dependency_hash.0 => {
                                (true, "a dependency file has changed".to_string())
                            }
                            Some(cache)
                                if driver.driver_hash(&cache.driver_dependencies)
                                    != cache.driver_hash.0 =>
                            {
                                (true, "the driver has changed".to_string())
                            }
                            Some(cache) => {
                                let mut hasher = blake3::Hasher::new();
                                let env = task.env.lock().unwrap();
                                for var in &cache.environment_dependencies {
                                    env.hash(var.as_str(), &mut hasher);
                                }
                                if hasher.finalize() != cache.environment_hash.0 {
                                    (true, "the environment has been modified".to_string())
                                } else {
                                    let mut outputs = cache.all_output.iter();
                                    loop {
                                        if let Some(output) = outputs.next() {
                                            if !output.is_file() && !output.is_dir() {
                                                break (
                                                    true,
                                                    format!("output file {} is missing", output),
                                                );
                                            }
                                        } else {
                                            match hash_output_files(
                                                &task.outputs,
                                                dependency_nodes,
                                                false,
                                            ) {
                                                Ok(out_hashes) => {
                                                    hashes = out_hashes;
                                                    break (
                                                        false,
                                                        "the task is up-to-date".to_string(),
                                                    );
                                                }
                                                Err(error) => break (true, error),
                                            }
                                        }
                                    }
                                }
                            }
                            None => (true, "the task has never been run".to_string()),
                        };

                        if do_run {
                            result_pipe
                                .send(WorkResult::TaskStart(
                                    task_index,
                                    thread_index,
                                    reason,
                                    driver.get_color(),
                                ))
                                .unwrap();
                            for n in &task.outputs {
                                n.parent().unwrap().mkdir().unwrap();
                            }
                            let mut output = driver.execute(task);

                            let hashes = if output.exit_code == 0 {
                                match hash_output_files(&task.outputs, dependency_nodes, false) {
                                    Ok(hashes) => hashes,
                                    Err(error) => {
                                        output.exit_code = 1;
                                        output.log = error;
                                        Vec::new()
                                    }
                                }
                            } else {
                                Vec::new()
                            };

                            let mut env_hasher = blake3::Hasher::new();
                            let env = &task.env;
                            let env = env.lock().unwrap();
                            let environment_dependencies = env.get_used_keys();
                            for var in &environment_dependencies {
                                env.hash(var.as_str(), &mut env_hasher);
                            }
                            result_pipe
                                .send(WorkResult::TaskResult(TaskResult {
                                    task_index,
                                    thread_index,
                                    exit_code: output.exit_code,
                                    command: output.command,
                                    log: output.log,
                                    output_hashes: hashes,
                                }))
                                .unwrap();
                            if output.exit_code == 0 {
                                dependency_pipe
                                    .send((
                                        task_index,
                                        DependencyRequest {
                                            file_dependencies: output.file_dependencies,
                                            input_hash,
                                            environment_dependencies,
                                            environment_hash: env_hasher.finalize(),
                                            driver_dependencies: output.driver_dependencies,
                                            driver_hash: SerializedHash(output.driver_hash),
                                            extra_output: output.extra_output,
                                        },
                                    ))
                                    .unwrap();
                            }
                        } else {
                            result_pipe
                                .send(WorkResult::TaskSkipped(task_index, hashes))
                                .unwrap();
                        }
                    }
                }
            }
        }
    }

    fn execute(
        &mut self,
        dependency_nodes: HashSet<Node>,
        tasks_cache: &[Option<TaskCacheEntry>],
        logger: &mut Logger,
        thread_count: usize,
        title: &str,
        progress_mode: u32,
    ) -> (Result<()>, Vec<Option<TaskCacheEntry>>) {
        let mut result_cache = vec![None; self.tasks_pool.len()];
        let mut thread_activity = ThreadActivity::new(thread_count);
        let mut input_hashes = Vec::new();
        let mut task_work = vec![(usize::MAX, false); self.tasks_pool.len()];

        let timer = time::Instant::now();
        if progress_mode >= 1 {
            log_progress(
                logger,
                title,
                thread_activity.get_graph(),
                0,
                self.target_tasks.len(),
                timer.elapsed(),
            );
        }
        fn cancel(index: usize, tasks: &[Task], task_work: &mut Vec<(usize, bool)>) -> usize {
            let mut result = 0;
            if !task_work[index].1 {
                task_work[index].1 = true;
                result += 1;
                for &index in &tasks[index].successors {
                    result += cancel(index, tasks, task_work);
                }
            }
            result
        }

        let mut longest_group = 1;
        for &task_index in &self.target_tasks {
            let task = &self.tasks_pool[task_index];
            task_work[task_index].0 = task.predecessors.len();
            longest_group = max(longest_group, task.driver.len());
        }

        let this = self as &Self;

        thread::scope(|scope| {
            let (send_request, receive_request) = crossbeam::channel::unbounded::<WorkRequest>();
            let (send_result, receive_result) = crossbeam::channel::unbounded::<WorkResult>();
            let (send_dep_request, receive_dep_request) =
                crossbeam::channel::unbounded::<(usize, DependencyRequest)>();
            let task_count: usize = self.target_tasks.len();
            let mut processed_tasks: usize = 0;

            let mut file_hashes = HashMap::new();

            fn add_input_dir(
                dir: &Node,
                input_hashes: &mut Vec<Node>,
                dependency_nodes: &HashSet<Node>,
            ) {
                for f in std::fs::read_dir(dir.path()).unwrap() {
                    let f = Node::from(&f.unwrap().path());
                    if !dependency_nodes.contains(&f) {
                        if !f.is_dir() {
                            input_hashes.push(f);
                        } else {
                            add_input_dir(&f, input_hashes, dependency_nodes);
                        }
                    }
                }
            }

            for &task in &self.target_tasks {
                for input in &self.tasks_pool[task].inputs {
                    if !dependency_nodes.contains(input) {
                        if input.is_dir() {
                            add_input_dir(input, &mut input_hashes, &dependency_nodes);
                        } else {
                            input_hashes.push(input.clone());
                        }
                    }
                }
                if let Some(cache) = &tasks_cache[task] {
                    for input in &cache.file_dependencies {
                        if !dependency_nodes.contains(input) {
                            input_hashes.push(input.clone());
                        }
                    }
                }
            }

            {
                /* captured values */
                let send = send_result.clone();
                let send_panic = send_result.clone();
                let receive = receive_dep_request.clone();

                scope.spawn(move || {
                    if let Err(_error) =
                        std::panic::catch_unwind(|| this.execute_dependency_thread(receive, send))
                    {
                        send_panic.send(WorkResult::Panic()).unwrap();
                    }
                });
            }

            for thread_index in 0..thread_count {
                /* captured values */
                let send = send_result.clone();
                let send_panic = send_result.clone();
                let receive = receive_request.clone();
                let dependency = send_dep_request.clone();
                let dependency_nodes = &dependency_nodes;

                scope.spawn(move || {
                    if let Err(_error) = std::panic::catch_unwind(|| {
                        this.execute_thread(
                            dependency_nodes,
                            tasks_cache,
                            thread_index,
                            receive,
                            send,
                            dependency,
                        )
                    }) {
                        send_panic.send(WorkResult::Panic()).unwrap();
                    }
                });
            }

            /* post all hashing requests */
            let request_count = thread_count * 3;
            let request_size = input_hashes.len() / request_count;
            let remainder = input_hashes.len() % request_count;
            let mut current = 0_usize;

            for i in 0..request_count {
                let request_size = request_size + (i < remainder) as usize;
                send_request
                    .send(WorkRequest::FileHash(
                        current,
                        &input_hashes[current..current + request_size],
                    ))
                    .unwrap();
                current += request_size;
            }

            /* wait for all hashing requests to have completed */
            for _ in 0..request_count {
                if let Ok(result) = receive_result.recv() {
                    match result {
                        WorkResult::FileHashResult(start, result) => {
                            for i in 0..result.len() {
                                // println!("~ {}", input_hashes[start + i]);
                                file_hashes.insert(input_hashes[start + i].clone(), result[i]);
                            }
                        }
                        WorkResult::Panic() => logger.error("Worker thread panicked"),
                        _ => unreachable!(),
                    }
                } else {
                    /* todo: error */
                }
            }

            let mut work_index = 0_usize;

            /* Post all tasks that do not have dependencies */
            for &task in &self.target_tasks {
                if task_work[task].0 == 0 {
                    self.on_task_ready(tasks_cache, &send_request, task, &file_hashes);
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
                                // println!("# {}", file);
                                file_hashes.insert(file, hash);
                            }

                            /* copy cache */
                            result_cache[task_index] = tasks_cache[task_index].clone();
                            for &successor in &self.tasks_pool[task_index].successors {
                                task_work[successor].0 -= 1;
                                if task_work[successor].0 == 0 {
                                    if !self.abort.load(Ordering::Acquire) {
                                        self.on_task_ready(
                                            tasks_cache,
                                            &send_request,
                                            successor,
                                            &file_hashes,
                                        );
                                    } else {
                                        processed_tasks += 1;
                                    }
                                }
                            }
                        }
                        WorkResult::TaskStart(task_index, thread_index, reason, color) => {
                            work_index += 1;
                            thread_activity.switch_on(thread_index);
                            let task = &self.tasks_pool[task_index];
                            logger.why_verbose(
                                format!("Running task {} because {}", task, reason).as_str(),
                            );
                            let id = if task.outputs.is_empty() {
                                if task.inputs.is_empty() {
                                    task.driver.clone()
                                } else {
                                    task.inputs[0].name()
                                }
                            } else {
                                task.outputs[0].name()
                            };
                            if progress_mode < 2 {
                                log_task_start(
                                    logger,
                                    work_index,
                                    task_count_str.as_str(),
                                    format!(
                                        "{{{}}}{:<width$}{{reset}} {}/{}",
                                        color,
                                        task.driver,
                                        task.generator,
                                        id,
                                        width = longest_group
                                    )
                                    .as_str(),
                                );
                            }
                        }
                        WorkResult::DependencyResult(task_index, result) => {
                            processed_tasks += 1;
                            result_cache[task_index] = Some(result);
                        }
                        WorkResult::TaskResult(result) => {
                            for (file, hash) in result.output_hashes {
                                file_hashes.insert(file.clone(), hash);
                            }
                            thread_activity.switch_off(result.thread_index);
                            let task = &self.tasks_pool[result.task_index];
                            log_task_end(
                                logger,
                                result.exit_code,
                                result.command.as_str(),
                                result.log.as_str(),
                            );
                            if result.exit_code != 0 {
                                self.abort.store(true, Ordering::Release);
                                processed_tasks += 1;
                                for &successor in &task.successors {
                                    processed_tasks +=
                                        cancel(successor, self.tasks_pool, &mut task_work);
                                }
                            } else {
                                for &successor in &task.successors {
                                    task_work[successor].0 -= 1;
                                    if task_work[successor].0 == 0 {
                                        self.on_task_ready(
                                            tasks_cache,
                                            &send_request,
                                            successor,
                                            &file_hashes,
                                        );
                                    }
                                }
                            }
                        }
                        WorkResult::TaskCanceled(task_index) => {
                            processed_tasks += 1;
                            for &successor in &self.tasks_pool[task_index].successors {
                                processed_tasks +=
                                    cancel(successor, self.tasks_pool, &mut task_work);
                            }
                        }
                        WorkResult::Panic() => {
                            logger.error("Worker thread panicked");
                            break;
                        }
                        _ => unreachable!(),
                    }
                } else {
                    /* todo: error */
                    logger.error("");
                }
                if progress_mode >= 1 {
                    log_progress(
                        logger,
                        title,
                        thread_activity.get_graph(),
                        processed_tasks,
                        task_count,
                        timer.elapsed(),
                    );
                }
            }
        });

        logger.clear_status();
        (Ok(()), result_cache)
    }

    fn on_task_ready(
        &self,
        tasks_cache: &[Option<TaskCacheEntry>],
        work_pipe: &Sender<WorkRequest>,
        task_index: usize,
        file_hashes: &HashMap<Node, blake3::Hash>,
    ) {
        let task = &self.tasks_pool[task_index];
        let mut input_hasher = blake3::Hasher::new();
        for input in &task.inputs {
            if input.is_dir() {
                for f in glob::glob(format!("{}/**/*", input).as_str())
                    .unwrap()
                    .flatten()
                {
                    if !f.is_dir() {
                        input_hasher.update(file_hashes.get(&Node::from(&f)).unwrap().as_bytes());
                    }
                }
            } else {
                input_hasher.update(file_hashes.get(input).unwrap().as_bytes());
            }
        }

        let mut dependency_hasher = blake3::Hasher::new();
        if let Some(cache) = &tasks_cache[task_index] {
            for input in &cache.file_dependencies {
                dependency_hasher.update(file_hashes.get(input).unwrap().as_bytes());
            }
        }

        work_pipe
            .send(WorkRequest::Run(
                task_index,
                input_hasher.finalize(),
                dependency_hasher.finalize(),
            ))
            .unwrap();
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
        ' ', '▖', '▘', '▌', '▗', '▄', '▚', '▙', '▝', '▞', '▀', '▛', '▐', '▟', '▜', '█',
    ];
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
            1 => self.thread_activity_graph[0] = '█',
            2 => self.thread_activity_graph[cell] = Self::GRAPH_HALF[self.thread_activity[cell]],
            _ => {
                self.thread_activity_graph[cell] = Self::GRAPH_QUARTERS[self.thread_activity[cell]]
            }
        }
    }

    fn switch_off(&mut self, index: usize) {
        let cell = index / 4;
        let index = index % 4;
        self.thread_activity[cell] &= !(1 << index);

        match self.thread_count {
            1 => self.thread_activity_graph[0] = ' ',
            2 => self.thread_activity_graph[cell] = Self::GRAPH_HALF[self.thread_activity[cell]],
            _ => {
                self.thread_activity_graph[cell] = Self::GRAPH_QUARTERS[self.thread_activity[cell]]
            }
        }
    }

    fn get_graph(&self) -> &[char] {
        self.thread_activity_graph.as_slice()
    }
}

fn log_task_start(logger: &mut Logger, index: usize, task_count: &str, message: &str) {
    logger.colored_println(
        format!(
            "[{:width$}/{}] {}",
            index,
            task_count,
            message,
            width = task_count.len()
        )
        .as_str(),
    );
}

fn log_task_end(logger: &mut Logger, result: u32, command: &str, message: &str) {
    if result != 0 {
        logger.error(
            format!(
                "{} returned exit code {} (0x{:08x})\n{}",
                command, result, result, message
            )
            .as_str(),
        );
    } else if !message.is_empty() {
        logger.colored_println(format!("{{dim}}{}{{reset}}", command).as_str());
        logger.print(message);
    } else {
        logger.info(command);
    }
}

const GRAPH_EIGTHS: [char; 7] = ['▏', '▎', '▍', '▌', '▋', '▊', '▉'];

fn log_progress(
    logger: &mut Logger,
    title: &str,
    thread_activity: &[char],
    finished_tasks: usize,
    task_count: usize,
    elapsed: Duration,
) {
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
    let progress_width = terminal_width - 8 - thread_activity.len();
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
            "{{bg:green}}▎{{black}}{}{{green}}{{bg:dark_grey}}{}▕{{reset}}{{bg:reset}}{{red}}{}{{reset}}▏{{green}}{:2}{}{:02}{{reset}}",
            &progress_bar[0..progress],
            &progress_bar[progress..progress_bar.len()],
            thread_activity.iter().collect::<String>(),
            v1, unit, v2).as_str());
    } else {
        logger.set_status(format!(
            "{{bg:green}}▎{{black}}{}{{green}}{{bg:dark_grey}}{}{}▕{{reset}}{{bg:reset}}{{red}}{}{{reset}}▏{{green}}{:2}{}{:02}{{reset}}",
            &progress_bar[0..progress],
            GRAPH_EIGTHS[remainder - 1],
            &progress_bar[progress + 1..progress_bar.len()],
            thread_activity.iter().collect::<String>(),
            v1, unit, v2).as_str());
    }
}

fn load_cache<T>(
    tasks_pool: &Vec<Task>,
    logger: &mut Logger,
    out_dir: &Path,
    groups: &[(String, T)],
) -> (
    Vec<Option<TaskCacheEntry>>,
    Vec<HashMap<SerializedHash, TaskCacheEntry>>,
) {
    let mut result = Vec::with_capacity(groups.len());
    let mut tasks_cache = Vec::new();
    tasks_cache.resize(tasks_pool.len(), None);
    for group in groups {
        let mut build_cache = BuildCache::new();
        let group_cache = out_dir.join(format!("{}.cache", group.0));
        if let Ok(mut file) = File::open(&group_cache) {
            match bincode::serde::decode_from_std_read(&mut file, bincode::config::standard())
                as std::result::Result<BuildCache, _>
            {
                Ok(group_cache) => {
                    build_cache = group_cache;
                }
                Err(error) => {
                    logger.warning(
                        format!(
                            "Unable to deserialize build cache {:?} ({})",
                            group_cache, error
                        )
                        .as_str(),
                    );
                }
            }
        }
        for (task, data) in zip(tasks_pool, &mut tasks_cache) {
            if let Some(cache) = build_cache.remove(&task.signature) {
                *data = Some(cache);
            }
        }
        result.push(build_cache);
    }
    (tasks_cache, result)
}

fn save_cache<T>(
    tasks_pool: &[Task],
    logger: &mut Logger,
    out_dir: &Path,
    groups: &[(String, T)],
    tasks_cache: &mut [Option<TaskCacheEntry>],
) {
    /* save all caches */
    for (group, _) in groups {
        let mut group_cache = HashMap::new();
        for (i, task) in tasks_pool.iter().enumerate() {
            if task.group.eq(group) {
                let mut entry = None;
                swap(&mut entry, &mut tasks_cache[i]);
                if let Some(cache) = entry {
                    group_cache.insert(task.signature.clone(), cache);
                }
            }
        }
        let cache_filename = out_dir.join(format!("{}.cache", group));
        match File::create(&cache_filename) {
            Ok(mut file) => {
                if let Err(e) = bincode::serde::encode_into_std_write(
                    group_cache,
                    &mut file,
                    bincode::config::standard(),
                ) {
                    logger.warning(
                        format!(
                            "Unable to serialize build cache {:?} ({})",
                            cache_filename, e
                        )
                        .as_str(),
                    );
                }
            }
            Err(e) => {
                logger.warning(
                    format!(
                        "Unable to serialize build cache {:?} ({})",
                        cache_filename, e
                    )
                    .as_str(),
                );
            }
        }
    }
}

fn hash_output_files(
    outputs: &[Node],
    dependency_nodes: &HashSet<Node>,
    mut is_dependency: bool,
) -> std::result::Result<Vec<(Node, blake3::Hash)>, String> {
    let mut hashes = Vec::new();
    for node in outputs {
        let mut hasher = blake3::Hasher::new();
        is_dependency = is_dependency || dependency_nodes.contains(node);
        if node.is_dir() {
            let content = std::fs::read_dir(node.path())
                .unwrap()
                .map(|x| Node::from(&x.unwrap().path()))
                .collect::<Vec<_>>();
            hashes.extend(hash_output_files(
                &content,
                dependency_nodes,
                is_dependency,
            )?);
        } else if is_dependency {
            if let Ok(file) = File::open(node.path()) {
                if hasher.update_reader(file).is_ok() {
                    hashes.push((node.clone(), hasher.finalize()));
                } else {
                    return Err(format!("output file `{}` could not be read", node));
                }
            } else {
                return Err(format!("output file `{}` is missing", node));
            }
        } else if !node.path().exists() {
            return Err(format!("output file `{}` is missing", node));
        }
    }
    Ok(hashes)
}
