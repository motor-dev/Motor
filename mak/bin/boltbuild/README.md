# Bolt⚡Build

[![Crates.io](https://img.shields.io/crates/v/boltbuild)](https://crates.io/crates/boltbuild)
[![Docs.rs](https://docs.rs/boltbuild/badge.svg)](https://docs.rs/boltbuild)
![License](https://img.shields.io/crates/l/boltbuild)

BoltBuild is a programmable build system that is designed to be fast and reliable.
It performs the steps usually done by a combination of `cmake`, `ninja`, `autotools`, and `configure`.
It is designed to build C/C++ projects, but its design is flexible enough to be used for other languages as well.

BoltBuild uses Lua as its configuration language, which allows for a high degree of flexibility.
The core of BoltBuild provides a set of functions that can be used to define build steps.
The build steps are implemented in Lua

# ⋮ Description

At the top level, BoltBuild runs a series of commands, starting with an implicit command called `init` that is always
run.
Each command can:

- define subsequent commands
- declare tasks that are queued for execution
- set environment variables that are passed to subsequent commands and tasks
- define dependencies between tasks

When a command has finished executing, tasks that have been declared by the command are executed in parallel.
Tasks are responsible for running the actual build steps, such as compiling source files, linking libraries, etc.

Running commands can often be skipped, as BoltBuild will cache the results of each command.
If BoltBuild determines that the script does not need to be executed, it will instead load all side effects from the
cache.
This allows for fast incremental builds. But the priority is on correctness, so BoltBuild will verify that the
environment is entirely identical before loading from the cache. In particular, a command will be rerun if any of the
following are true:

- If the command has never been run before,
- If any Lua script loaded by the command has changed,
- If any of the environment variables used by the script have changed,
- If any of the command line options used by the script differ from the previous run,
- If any search on the filesystem would return different results than the previous run.
- If the user specifies that the command should always be rerun.

If none of the above are true, BoltBuild will load the command results from the cache and start to execute tasks.

Each task result is also cached, so if a task has already been run, it will not be run again unless the task has
changed.
The task is considered to have changed if any of the following are true:

- if the task has never been run before,
- if any of the files that the task explicitely depends on have changed,
- if any of the files that the task listed as implicit dependencies have changed,
- if any of the files that the task generates have been deleted,
- if the driver script has changed,
- if the environment variables used by the task have changed.

# 🔩 Features

- **Fast**: BoltBuild is designed to be fast. It will only run the commands that are necessary to build the project.
- **Reliable**: BoltBuild will verify that the environment is identical before loading from the cache.
- **Incremental**: BoltBuild will only run the tasks that have changed.
- **Parallel**: BoltBuild will run tasks in parallel.
- **Flexible**: BoltBuild uses Lua as its configuration language, which allows for a high degree of flexibility.
- **Cross-platform**: BoltBuild is designed to work on all platforms that Rust supports.
- **Extensible**: BoltBuild is designed to be extensible. It is easy to add new commands and tasks.
