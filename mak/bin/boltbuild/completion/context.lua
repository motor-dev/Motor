---@meta

local function use(var)
    return var
end

---@class Context
---@field name string The name of the command
---@field fun string The name of the function to run.
---@field env Environment
---@field path Node
---@field src_dir Node
---@field bld_dir Node
---@field settings Settings
---@field [string] any
Context = {}

---Loads a tool file. Tools work in a similar way to `recurse`, but they are also automatically loaded by dependent commands.
---@param tool_name string The name of the tool. RsWaf wil lscan through the tools_dir setting to find a file called `tool_name`.lua
---@param reload boolean? Whether the tool should be loaded again if it was already loaded. If not specified, the tool is not reloaded.
function Context:load_tool(tool_name, reload)
    use(tool_name)
    use(reload)
end

---Executes the script located at `path`.
---If `path` is a directory, the function will look for a file with the basename `context.fun` in that directory.
---@param path string A path, absolute or relative to the current context's path
function Context:recurse(path)
    use(path)
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
