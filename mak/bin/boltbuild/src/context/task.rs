use super::Context;
use crate::node::Node;
use crate::task::Task;
use mlua::prelude::{LuaError, LuaResult};
use mlua::Result;
use std::collections::hash_map::Entry;
use std::collections::HashSet;

impl Context {
    pub(crate) fn declare_products(
        &mut self,
        nodes: &Vec<Node>,
        mut new_dependencies: Vec<(usize, usize, String)>,
        task_index: usize,
        new_task: Option<Task>,
    ) -> LuaResult<()> {
        for node in nodes {
            if self.products.contains_key(node) {
                let task = &self.tasks[self.products[node]];
                return Err(LuaError::RuntimeError(format!(
                    "cannot declare product {}: already a product of task\n  {}",
                    node, task
                )));
            }
            for (index, task) in self.tasks.iter().enumerate() {
                if task.inputs.iter().any(|x| x == node) {
                    new_dependencies.push((task_index, index, format!("dependency on {}", node)));
                }
            }
        }

        self.add_dependencies(new_dependencies, new_task)?;

        for node in nodes {
            /* in case the same node is added twice */
            match self.products.entry(node.clone()) {
                Entry::Vacant(vacant_entry) => {
                    vacant_entry.insert(task_index);
                }
                Entry::Occupied(_) => (),
            }
        }
        Ok(())
    }

    pub(crate) fn add_dependencies(
        &mut self,
        dependencies: Vec<(usize, usize, String)>,
        new_task: Option<Task>,
    ) -> Result<()> {
        let mut new_dependencies = dependencies.clone();
        if !new_dependencies.is_empty() {
            let mut commit_dependencies = Vec::new();
            new_dependencies.sort();
            while !new_dependencies.is_empty() {
                let (producer, consumer, reason) = new_dependencies.remove(0);
                let mut set = vec![(producer, consumer, reason)];
                while !new_dependencies.is_empty() {
                    if producer == new_dependencies[0].0 {
                        set.push(new_dependencies.remove(0));
                    } else {
                        break;
                    }
                }
                self.add_dependency_set(&set, &commit_dependencies, new_task.as_ref())?;
                commit_dependencies.extend(set);
            }
            if let Some(new_task) = new_task {
                self.task_dependencies.push(Vec::new());
                self.tasks.push(new_task);
            }
            for (predecessor, successor, _) in dependencies {
                self.tasks[predecessor].successors.push(successor);
                self.tasks[successor].predecessors.push(predecessor);
            }
            for (producer, consumer, reason) in commit_dependencies {
                self.task_dependencies[producer].push((consumer, reason));
            }
        } else if let Some(new_task) = new_task {
            self.task_dependencies.push(Vec::new());
            self.tasks.push(new_task);
        }

        Ok(())
    }

    fn add_dependency_set(
        &mut self,
        new_dependencies: &[(usize, usize, String)],
        committed_dependencies: &[(usize, usize, String)],
        new_task: Option<&Task>,
    ) -> Result<()> {
        let mut start = HashSet::new();
        let mut queue = Vec::new();
        let mut seen = HashSet::new();
        for (producer, consumer, reason) in new_dependencies {
            start.insert(*producer);
            queue.push((*consumer, vec![(*producer, reason)]));
        }

        while let Some(item) = queue.pop() {
            let (producer, path) = item;
            if start.contains(&producer) {
                return Err(LuaError::RuntimeError(format!(
                    "Cycle detected in task dependency:\n  {}\n  {}",
                    path.iter()
                        .map(|x| format!(
                            "{}\n    ({})",
                            self.tasks.get(x.0).or(new_task).unwrap(),
                            x.1
                        ))
                        .collect::<Vec<_>>()
                        .join("\n  "),
                    self.tasks.get(producer).or(new_task).unwrap()
                )));
            }

            if producer < self.task_dependencies.len() {
                for (consumer, reason) in &self.task_dependencies[producer] {
                    if seen.contains(consumer) {
                        continue;
                    }
                    seen.insert(*consumer);
                    let mut path = path.clone();
                    path.push((producer, reason));
                    queue.push((*consumer, path));
                }
                for (p, consumer, reason) in committed_dependencies.iter() {
                    if *p == producer {
                        if seen.contains(consumer) {
                            continue;
                        }
                        seen.insert(*consumer);
                        let mut path = path.clone();
                        path.push((*p, reason));
                        queue.push((*consumer, path));
                    }
                }
            }
        }

        Ok(())
    }
}
