---@meta

--- The `Context` class provides core functions for managing build commands, environments, tasks, and filesystem access.
--- It centralizes the configuration and execution settings needed across commands in the build system.
---@class Context
---@field name string The name of the command being executed.
---@field fs_name string The filesystem name associated with the command.
---@field fun string The function name to run in this context.
---@field env Environment The environment object with configuration details for the command.
---@field path Node The current path of the context's operation.
---@field src_dir Node The source directory for this command or build.
---@field bld_dir Node The build directory for storing output.
---@field settings Settings Command-line options and settings shared across contexts.
Context = {}
