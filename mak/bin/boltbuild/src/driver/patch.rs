use crate::driver::Output;
use crate::node::Node;
use crate::task::Task;
use serde::{Deserialize, Serialize};
use std::ffi::OsStr;
use std::fs::File;
use std::io::{Read, Write};
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
pub(super) struct PatchDriverConfiguration {}

impl PatchDriverConfiguration {
    pub(super) fn new() -> Self {
        Self {}
    }

    pub(super) fn execute(&self, task: &Task) -> Output {
        let driver_hash = self.hash(&[]);
        let strip = task.env.lock().unwrap().get("PATCH_STRIP").as_int();

        if task.inputs.len() < 2 {
            return Output {
                exit_code: 1,
                command: "patch".to_string(),
                log: "Expected an input path and one or more patches".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }
        let input_path = &task.inputs[0];

        let patches = &task.inputs[1..];

        if task.outputs.len() != 1 {
            return Output {
                exit_code: 1,
                command: format!("patch {}", input_path),
                log: "Expected one output path".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }
        let output_path = &task.outputs[0];
        if let Err(e) = if input_path.is_dir() {
            output_path.mkdir()
        } else {
            output_path.parent().unwrap().mkdir()
        } {
            return Output {
                exit_code: 1,
                command: format!("patch {} => {}", input_path, output_path),
                log: e.to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            };
        }

        let command = format!("patch {} => {}", input_path, output_path);

        match patch(input_path, output_path, patches, strip) {
            Ok(result) => Output {
                exit_code: 0,
                command,
                log: "".to_string(),
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: result,
            },
            Err(x) => Output {
                exit_code: 1,
                command,
                log: x,
                driver_hash,
                driver_dependencies: Vec::new(),
                file_dependencies: Vec::new(),
                extra_output: Vec::new(),
            },
        }
    }

    pub(super) fn hash(&self, _: &[Node]) -> blake3::Hash {
        blake3::Hasher::new()
            .update("version:1.0".as_bytes())
            .finalize()
    }
}

fn patch(
    input_path: &Node,
    output_path: &Node,
    patches: &[Node],
    strip: i64,
) -> Result<Vec<Node>, String> {
    let mut outputs = Vec::new();
    let input_nodes = if input_path.is_dir() {
        glob::glob(format!("{}/**/*", input_path).as_str())
            .map_err(|e| format!("Failed to glob input path: {}", e))?
            .filter_map(|x| {
                if let Ok(p) = x {
                    if !p.is_dir() {
                        Some(Node::from(&p))
                    } else {
                        None
                    }
                } else {
                    None
                }
            })
            .collect()
    } else {
        vec![input_path.clone()]
    };

    for patch in patches {
        let mut file = File::open(patch.abs_path())
            .map_err(|e| format!("Failed to open patch file `{}`: {}", patch, e))?;
        let mut content = Vec::new();
        file.read_to_end(&mut content)
            .map_err(|e| format!("Failed to read patch file `{}`: {}", patch, e))?;
        let diff = String::from_utf8(content)
            .map_err(|e| format!("Failed to parse patch file `{}`: {}", patch, e))?;

        let mut lines = diff.as_str().lines();
        let mut diff_start = diff.as_str().as_ptr();
        let mut line_count = 0_usize;

        if let Some(mut line) = lines.next() {
            line_count += 1;
            'diff: loop {
                if line.is_empty() {
                    if Some(line) == lines.next() {
                        continue;
                    } else {
                        break;
                    }
                }
                if !line.starts_with("---") && !line.starts_with("+++") {
                    line = lines.next().ok_or("Unexpected end of patch file")?;
                    line_count += 1;
                }
                if line.starts_with("---") {
                    line = lines.next().ok_or("Unexpected end of patch file")?;
                    line_count += 1;
                    if line.starts_with("+++") {
                        line = lines.next().ok_or("Unexpected end of patch file")?;
                        line_count += 1;
                    }
                } else if line.starts_with("+++") {
                    line = lines.next().ok_or("Unexpected end of patch file")?;
                    line_count += 1;
                    if line.starts_with("---") {
                        line = lines.next().ok_or("Unexpected end of patch file")?;
                        line_count += 1;
                    }
                }

                if line.starts_with("@@") {
                    for hunk_line in lines.by_ref() {
                        line_count += 1;
                        if !hunk_line.starts_with(" ")
                            && !hunk_line.starts_with("+")
                            && !hunk_line.starts_with("-")
                            && !hunk_line.starts_with("@@")
                        {
                            line = hunk_line;
                            let diff_end = line.as_ptr();
                            if let Some(r) = run_patch(
                                patch,
                                input_path,
                                output_path,
                                &mut outputs,
                                diff_start,
                                diff_end,
                                strip,
                            )? {
                                outputs.push(r);
                            }
                            diff_start = diff_end;
                            continue 'diff;
                        }
                    }
                    let diff_end = diff.as_str().as_ptr().wrapping_add(diff.len());
                    if let Some(r) = run_patch(
                        patch,
                        input_path,
                        output_path,
                        &mut outputs,
                        diff_start,
                        diff_end,
                        strip,
                    )? {
                        outputs.push(r);
                    }
                    break 'diff;
                } else {
                    return Err(format!(
                        "Unexpected input in patch file at line {}",
                        line_count
                    ));
                }
            }
        }
    }

    for (_, node, content) in outputs.iter() {
        node.parent().unwrap().mkdir().map_err(|e| {
            format!(
                "Failed to create directory `{}`: {}",
                node.parent().unwrap(),
                e
            )
        })?;
        let mut file =
            File::create(node.abs_path()).map_err(|e| format!("Failed to create file: {}", e))?;
        file.write_all(content)
            .map_err(|e| format!("Failed to write file: {}", e))?;
    }

    'copy: for input_node in input_nodes {
        for (node, _, _) in outputs.iter() {
            if &input_node == node {
                continue 'copy;
            }
        }
        let mut content = Vec::new();
        let mut file = File::open(input_node.abs_path())
            .map_err(|e| format!("Failed to open input file `{}`: {}", input_node, e))?;
        file.read_to_end(&mut content)
            .map_err(|e| format!("Failed to read input file `{}`: {}", input_node, e))?;
        let output_node = output_path.make_node(&PathBuf::from(
            input_node
                .path()
                .strip_prefix(input_path.path())
                .map_err(|e| format!("Failed to strip prefix from path: {}", e))?,
        ));
        output_node.parent().unwrap().mkdir().map_err(|e| {
            format!(
                "Failed to create directory `{}`: {}",
                output_node.parent().unwrap(),
                e
            )
        })?;
        let mut file = File::create(output_node.abs_path())
            .map_err(|e| format!("Failed to create output file `{}`: {}", output_node, e))?;
        file.write_all(&content)
            .map_err(|e| format!("Failed to write output file `{}`: {}", output_node, e))?;
        outputs.push((input_node, output_node, Vec::new()));
    }
    Ok(outputs.into_iter().map(|(_, node, _)| node).collect())
}

fn run_patch(
    patch_file: &Node,
    input_path: &Node,
    output_path: &Node,
    outputs: &mut [(Node, Node, Vec<u8>)],
    diff_start: *const u8,
    diff_end: *const u8,
    strip: i64,
) -> Result<Option<(Node, Node, Vec<u8>)>, String> {
    let patch = diffy::Patch::from_bytes(unsafe {
        std::slice::from_raw_parts(diff_start, diff_end as usize - diff_start as usize)
    })
    .map_err(|e| format!("Failed to parse patch: {}", e))?;

    let input_file_name =
        PathBuf::from(unsafe { OsStr::from_encoded_bytes_unchecked(patch.original().unwrap()) });
    let output_file_name =
        PathBuf::from(unsafe { OsStr::from_encoded_bytes_unchecked(patch.modified().unwrap()) });

    let input_file_name = if strip > 0 {
        input_file_name.iter().skip(strip as usize).collect()
    } else {
        input_file_name
    };
    let output_file_name = if strip > 0 {
        output_file_name.iter().skip(strip as usize).collect()
    } else {
        output_file_name
    };

    let input_node = input_path.make_node(&input_file_name);
    let output_node = output_path.make_node(&output_file_name);

    for (patched_input_node, patched_output_node, content) in outputs.iter_mut() {
        if (patched_input_node == &input_node) || (patched_output_node == &output_node) {
            let new_content = diffy::apply_bytes(content, &patch).map_err(|e| {
                format!(
                    "Failed to apply patch `{}` onto input file `{}`: {}",
                    patch_file, input_node, e
                )
            })?;
            *content = new_content;
            return Ok(None);
        }
    }
    let mut content = Vec::new();
    let mut file = File::open(input_node.abs_path())
        .map_err(|e| format!("Failed to open input file `{}`: {}", input_node, e))?;
    file.read_to_end(&mut content)
        .map_err(|e| format!("Failed to read input file `{}`: {}", input_node, e))?;
    let new_content = diffy::apply_bytes(&content, &patch).map_err(|e| {
        format!(
            "Failed to apply patch `{}` onto input file `{}`: {}",
            patch_file, input_node, e
        )
    })?;

    Ok(Some((input_node, output_node, new_content)))
}
