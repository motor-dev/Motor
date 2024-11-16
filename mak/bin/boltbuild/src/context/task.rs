use std::collections::hash_map::Entry;
use mlua::prelude::{LuaError, LuaResult};
use super::Context;
use mlua::Result;
use crate::node::Node;
use crate::task::Task;

impl Context {
    pub(crate) fn declare_products(&mut self, nodes: &Vec<Node>, mut new_dependencies: Vec<(usize, usize, String)>, task_index: usize, new_task: Option<&Task>) -> LuaResult<()> {
        for node in nodes {
            if self.products.contains_key(node.path()) {
                let task = &self.tasks[self.products[node.path()]];
                return Err(LuaError::RuntimeError(format!("cannot declared product {}: already a product of task\n  {}", node, task)));
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
            match self.products.entry(node.path().clone()) {
                Entry::Vacant(vacant_entry) => {
                    vacant_entry.insert(task_index);
                }
                Entry::Occupied(_) => (),
            }
        }
        Ok(())
    }

    pub(crate) fn add_dependencies(&mut self, new_dependencies: Vec<(usize, usize, String)>, new_task: Option<&Task>) -> Result<()> {
        if !new_dependencies.is_empty() {
            let mut result = Vec::new();
            let mut edges = self.task_dependencies.clone();
            edges.extend(new_dependencies.clone());

            let mut roots = Vec::new();

            for i in 0..self.tasks.len() {
                if !edges.iter().any(|edge| edge.1 == i) {
                    roots.push(i);
                }
            }


            if new_task.is_some() {
                let i = self.tasks.len();
                if !edges.iter().any(|edge| edge.1 == i) {
                    roots.push(i);
                }
            }

            while let Some(root) = roots.pop() {
                while let Some(edge_index) = edges.iter().position(|x| x.0.eq(&root)) {
                    let edge = edges.swap_remove(edge_index);
                    if !edges.iter().any(|e| e.1.eq(&edge.1)) {
                        roots.push(edge.1);
                    }
                }
                result.push(root);
            }

            if !edges.is_empty() {
                edges.sort();
                Err(LuaError::RuntimeError(format!("Cycle detected in task dependency:\n  {}",
                                                   edges.iter()
                                                       .map(|x| format!("{}\n  {}\n    ({})",
                                                                        self.tasks.get(x.0).or(new_task).unwrap(),
                                                                        self.tasks.get(x.1).or(new_task).unwrap(),
                                                                        x.2)).collect::<Vec<_>>().join("\n  "))))
            } else {
                self.task_dependencies.extend(new_dependencies);
                Ok(())
            }
        } else {
            Ok(())
        }
    }
}