---@meta

local function use(var)
    return var
end

---@class Context
--- The `Context` class provides core functions for managing build commands, environments, tasks, and filesystem access.
--- It centralizes the configuration and execution settings needed across commands in the build system.
---
---@field name string The name of the command being executed.
---@field fs_name string The filesystem name associated with the command.
---@field fun string The function name to run in this context.
---@field env Environment The environment object with configuration details for the command.
---@field path Node The current path of the context's operation.
---@field src_dir Node The source directory for this command or build.
---@field bld_dir Node The build directory for storing output.
---@field settings Settings Command-line options and settings shared across contexts.
---@field [string] any Used to support dynamic indexing within the context object.
Context = {}

--- Recursively loads or executes the script at the specified `path`.
--- - If `path` is a file, it will be executed directly.
--- - If `path` is a directory, the function will search for a file named after the `context.fun` basename in that directory
---   (e.g., if `context.fun` is `"build"`, it will look for `build.lua`).
---
---@param path string The path to the file or directory, either absolute or relative to the context's current path.
function Context:recurse(path)
    use(path)
end

---Loads a tool file. Tools work in a similar way to `recurse`, but they are also automatically loaded by dependent commands.
---@param tool_name string The name of the tool. RsWaf wil lscan through the tools_dir setting to find a file called `tool_name`.lua
---@param reload boolean? Whether the tool should be loaded again if it was already loaded. If not specified, the tool is not reloaded.
function Context:load_tool(tool_name, reload)
    use(tool_name)
    use(reload)
end



---A commend that has been declared
---@class DeclaredCommand
local DeclaredCommand = {}

---Declares a new command.
---@param name string The name of the command. Two different commands cannot have the same name. Corresponds to `Context.name`.
---@param fun string The name of a function. Corresponds to `Context.fun`.
---@param envs Environment|Environment[] An environment or a list of environments that will be available for this command. \
---                                      The command will receive derived environments that inherit these environments.
---@return DeclaredCommand An object that represents the declared command, which allows chaining declarations.
function Context:declare_command(name, fun, envs)
    use(name)
    use(fun)
    use(envs)
    return DeclaredCommand
end

---Declares a new command that will be formally declared by a subsequent command.
---This allows declaring commands depending of commands that have not run yet.
---The new command will be known by `rswaf` and if the depending command has not been run, it will be run first.
---@param depending DeclaredCommand The name of the command. Two different commands cannot have the same name. Corresponds to `Context.name`.
---@param name string The name of the command. Two different commands cannot have the same name. Corresponds to `Context.name`.
---@param fun string The name of a function. Corresponds to `Context.fun`.
---@return DeclaredCommand An object that represents the declared command, which allows chaining declarations.
function Context:chain_command(depending, name, fun)
    use(name)
    use(fun)
    return depending
end
