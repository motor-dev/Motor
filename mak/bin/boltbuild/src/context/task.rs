use super::{Context, NodeData};
use crate::node::Node;
use crate::task::Task;
use mlua::prelude::{LuaError, LuaResult};
use mlua::Result;
use std::collections::hash_map::Entry;
use std::collections::{HashMap, HashSet};

type Dependency = (usize, usize, String);

impl Context {
    pub(crate) fn declare_task(&mut self, task: Task) -> LuaResult<usize> {
        let task_index = self.tasks.len();
        let mut dependencies = Vec::new();

        for (predecessor, successor) in &self.driver_order {
            if predecessor.eq(&task.driver) {
                if let Some(tasks) = self.driver_tasks.get(successor) {
                    for &task in tasks {
                        dependencies.push((
                            task_index,
                            task,
                            format!("dependency {} -> {}", predecessor, successor),
                        ));
                    }
                }
            } else if successor.eq(&task.driver) {
                if let Some(tasks) = self.driver_tasks.get(predecessor) {
                    for &task in tasks {
                        dependencies.push((
                            task,
                            task_index,
                            format!("dependency {} -> {}", predecessor, successor),
                        ));
                    }
                }
            }
        }

        self.tasks.push(task);
        self.task_dependencies.push(Vec::new());

        let task = &self.tasks[task_index];
        if let Err(e) = self.apply_dependencies(
            task_index,
            dependencies,
            &task.inputs.clone(),
            &task.outputs.clone(),
        ) {
            self.tasks.pop();
            self.task_dependencies.pop();
            Err(e)
        } else {
            Ok(task_index)
        }
    }

    pub(crate) fn add_inputs(&mut self, task_index: usize, new_inputs: &[Node]) -> LuaResult<()> {
        self.apply_dependencies(task_index, Vec::new(), new_inputs, &[])
    }

    pub(crate) fn add_outputs(&mut self, task_index: usize, new_outputs: &[Node]) -> LuaResult<()> {
        self.apply_dependencies(task_index, Vec::new(), &[], new_outputs)
    }

    pub(crate) fn add_dependencies(&mut self, dependencies: Vec<Dependency>) -> LuaResult<()> {
        let dependencies = self.verify_dependencies(dependencies)?;
        for (predecessor, successor, _) in &dependencies {
            self.tasks[*predecessor].successors.push(*successor);
            self.tasks[*successor].predecessors.push(*predecessor);
        }
        for (producer, consumer, reason) in dependencies {
            self.task_dependencies[producer].push((consumer, reason));
        }
        Ok(())
    }

    fn apply_dependencies(
        &mut self,
        task_index: usize,
        dependencies: Vec<Dependency>,
        inputs: &[Node],
        outputs: &[Node],
    ) -> LuaResult<()> {
        match self.gather_dependencies(task_index, dependencies, inputs, outputs) {
            Err(e) => {
                /* undo, return error */
                self.tasks.pop();
                self.task_dependencies.pop();
                Err(e)
            }
            Ok((dependencies, products)) => {
                let dependencies = self.verify_dependencies(dependencies)?;
                for (predecessor, successor, _) in &dependencies {
                    self.tasks[*predecessor].successors.push(*successor);
                    self.tasks[*successor].predecessors.push(*predecessor);
                }
                for (producer, consumer, reason) in dependencies {
                    self.task_dependencies[producer].push((consumer, reason));
                }

                for (node, node_data) in products {
                    match self.products.entry(node) {
                        Entry::Vacant(vacant_entry) => {
                            vacant_entry.insert(node_data);
                        }
                        Entry::Occupied(mut occupied_entry) => {
                            occupied_entry.get_mut().producer = node_data.producer;
                            occupied_entry
                                .get_mut()
                                .contributors
                                .extend(node_data.contributors);
                            occupied_entry
                                .get_mut()
                                .direct_consumers
                                .extend(node_data.direct_consumers);
                            occupied_entry
                                .get_mut()
                                .indirect_consumers
                                .extend(node_data.indirect_consumers);
                        }
                    }
                }

                Ok(())
            }
        }
    }

    fn gather_dependencies(
        &self,
        task_index: usize,
        mut new_dependencies: Vec<Dependency>,
        inputs: &[Node],
        outputs: &[Node],
    ) -> LuaResult<(Vec<Dependency>, HashMap<Node, NodeData>)> {
        let mut new_products = HashMap::new();

        /* declare all inputs and hook up all dependencies onto existing outputs */
        for node in inputs {
            if let Some(node_data) = self.products.get(node) {
                if let Some(producer) = node_data.producer {
                    new_dependencies.push((producer, task_index, format!("input {}", node)))
                }
                for contributor in &node_data.contributors {
                    new_dependencies.push((*contributor, task_index, format!("input {}", node)))
                }
            }

            match new_products.entry(node.clone()) {
                Entry::Vacant(vacant_entry) => {
                    vacant_entry.insert(NodeData {
                        producer: None,
                        contributors: HashSet::new(),
                        direct_consumers: HashSet::from([task_index]),
                        indirect_consumers: HashSet::new(),
                    });
                }
                Entry::Occupied(mut occupied_entry) => {
                    if let Some(producer) = occupied_entry.get().producer {
                        new_dependencies.push((producer, task_index, format!("input {}", node)))
                    }
                    for contributor in &occupied_entry.get().contributors {
                        new_dependencies.push((*contributor, task_index, format!("input {}", node)))
                    }
                    occupied_entry.get_mut().direct_consumers.insert(task_index);
                }
            }

            let mut maybe_parent_node = node.parent();
            while let Some(parent_node) = maybe_parent_node {
                if let Some(node_data) = self.products.get(&parent_node) {
                    if let Some(producer) = node_data.producer {
                        new_dependencies.push((producer, task_index, format!("input {}", node)))
                    }
                }

                match new_products.entry(parent_node.clone()) {
                    Entry::Vacant(vacant_entry) => {
                        vacant_entry.insert(NodeData {
                            producer: None,
                            contributors: HashSet::new(),
                            direct_consumers: HashSet::new(),
                            indirect_consumers: HashSet::from([task_index]),
                        });
                    }
                    Entry::Occupied(mut occupied_entry) => {
                        if let Some(producer) = occupied_entry.get().producer {
                            new_dependencies.push((producer, task_index, format!("input {}", node)))
                        }
                        occupied_entry
                            .get_mut()
                            .indirect_consumers
                            .insert(task_index);
                    }
                }

                maybe_parent_node = parent_node.parent();
            }
        }

        /* declare all outputs, add dependency on all declared inputs */
        for node in outputs {
            /* verify that there is no overlap in the declared products */
            if let Some(node_data) = self.products.get(node) {
                if let Some(producer) = node_data.producer {
                    let task = &self.tasks[producer];
                    return Err(LuaError::RuntimeError(format!(
                        "cannot declare product {}: already a product of task\n  {}",
                        node, task
                    )));
                } else if !node_data.contributors.is_empty() {
                    let tasks = node_data
                        .contributors
                        .iter()
                        .map(|x| self.tasks[*x].to_string())
                        .collect::<Vec<_>>()
                        .join("\n  ");
                    return Err(LuaError::RuntimeError(format!(
                        "cannot declare product {}: already a contributor to tasks\n  {}",
                        node, tasks
                    )));
                }
                for consumer in &node_data.direct_consumers {
                    new_dependencies.push((task_index, *consumer, format!("input {}", node)))
                }
                for consumer in &node_data.indirect_consumers {
                    new_dependencies.push((task_index, *consumer, format!("input {}", node)))
                }
            }

            match new_products.entry(node.clone()) {
                Entry::Vacant(vacant_entry) => {
                    vacant_entry.insert(NodeData {
                        producer: Some(task_index),
                        contributors: HashSet::new(),
                        direct_consumers: HashSet::new(),
                        indirect_consumers: HashSet::new(),
                    });
                }
                Entry::Occupied(mut occupied_entry) => {
                    if !occupied_entry.get().contributors.is_empty() {
                        let tasks = occupied_entry
                            .get()
                            .contributors
                            .iter()
                            .map(|x| self.tasks[*x].to_string())
                            .collect::<Vec<_>>()
                            .join("\n  ");
                        return Err(LuaError::RuntimeError(format!(
                            "cannot declare product {}: already a contributor to tasks\n  {}",
                            node, tasks
                        )));
                    }
                    for consumer in &occupied_entry.get().direct_consumers {
                        new_dependencies.push((task_index, *consumer, format!("input {}", node)))
                    }
                    for consumer in &occupied_entry.get().indirect_consumers {
                        new_dependencies.push((task_index, *consumer, format!("input {}", node)))
                    }
                    occupied_entry.get_mut().producer = Some(task_index);
                }
            }

            let mut maybe_parent_node = node.parent();
            while let Some(parent_node) = maybe_parent_node {
                if let Some(node_data) = self.products.get(&parent_node) {
                    if let Some(producer) = node_data.producer {
                        let task = &self.tasks[producer];
                        return Err(LuaError::RuntimeError(format!(
                            "cannot declare product {}: parent directory {} already a product of task\n  {}",
                            node, parent_node, task
                        )));
                    }
                    for consumer in &node_data.direct_consumers {
                        new_dependencies.push((task_index, *consumer, format!("input {}", node)))
                    }
                }

                match new_products.entry(parent_node.clone()) {
                    Entry::Vacant(vacant_entry) => {
                        vacant_entry.insert(NodeData {
                            producer: None,
                            contributors: HashSet::from([task_index]),
                            direct_consumers: HashSet::new(),
                            indirect_consumers: HashSet::new(),
                        });
                    }
                    Entry::Occupied(mut occupied_entry) => {
                        if let Some(producer) = occupied_entry.get().producer {
                            let task = &self.tasks[producer];
                            return Err(LuaError::RuntimeError(format!(
                                "cannot declare product {}: parent directory {} already a product of task\n  {}",
                                node, parent_node, task
                            )));
                        }
                        for consumer in &occupied_entry.get().direct_consumers {
                            new_dependencies.push((
                                task_index,
                                *consumer,
                                format!("input {}", node),
                            ))
                        }
                        occupied_entry.get_mut().contributors.insert(task_index);
                    }
                }
                maybe_parent_node = parent_node.parent();
            }
        }

        Ok((new_dependencies, new_products))
    }

    pub(crate) fn verify_dependencies(
        &self,
        mut dependencies: Vec<Dependency>,
    ) -> Result<Vec<Dependency>> {
        let mut commit_dependencies = Vec::new();
        if !dependencies.is_empty() {
            dependencies.sort();
            while !dependencies.is_empty() {
                let (producer, consumer, reason) = dependencies.remove(0);
                let mut set = vec![(producer, consumer, reason)];
                while !dependencies.is_empty() {
                    if producer == dependencies[0].0 {
                        set.push(dependencies.remove(0));
                    } else {
                        break;
                    }
                }
                self.verify_dependency_set(&set, &commit_dependencies)?;
                commit_dependencies.extend(set);
            }
        }

        Ok(commit_dependencies)
    }

    fn verify_dependency_set(
        &self,
        new_dependencies: &[Dependency],
        committed_dependencies: &[Dependency],
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
                        .map(|x| format!("{}\n    ({})", self.tasks[x.0], x.1))
                        .collect::<Vec<_>>()
                        .join("\n  "),
                    self.tasks[producer]
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
