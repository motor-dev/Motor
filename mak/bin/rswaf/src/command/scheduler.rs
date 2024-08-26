use super::Command;

use crate::error::Result;
use crate::task::Task;
use std::thread;

impl Command {
    fn execute(tasks: Vec<Task>, thread_count: usize) -> Result<()> {
        let (send_task, receive_task) = crossbeam::channel::unbounded::<Task>();
        let (send_result, receive_result) = crossbeam::channel::unbounded::<Task>();

        //let mut task_count: usize = tasks.len();
        let mut sent_tasks: usize = 0;
        let mut received_tasks: usize = 0;

        for i in 0..thread_count {
            let send = send_result.clone();
            let receive = receive_task.clone();
            thread::Builder::new().name(format!("worker {}", i)).spawn(move || {
                /* todo: start lua context here */
                let task = receive.recv();
                if let Ok(task) = task {
                    send.send(task).unwrap();
                }
            })?;
        }

        for task in tasks {
            /* todo: check inputs, check deps, etc */
            sent_tasks += 1;
            send_task.send(task).unwrap();
        }

        while sent_tasks != received_tasks {
            let task = receive_result.recv().unwrap();

            received_tasks += 1;

            /* todo: post tasks that depend on this */
        }

        Ok(())
    }
}