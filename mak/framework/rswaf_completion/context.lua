---@meta

local function use(var)return var end

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

---Executes the script located at `path`.
---If `path` is a directory, executes a lua script called `context.fun` in this directory.
---@param path string A path, absolute or relative to the current context's path
function Context:recurse(path)use(path) end

---Creates a new environment that inherits from the specified environment.
---@param env Environment the base environment.
---@return Environment a new Environment that inherits the values from env.
function Context:derive(env) return env end

---Search for files on the filesystem. Using `directory` as a starting point, returns all files (as `Node` objects) that
---match the given pattern. Additionally, the search result is stored and will be used to check if a context is
---up-to-date.
---@param directory Node The root directory of the search
---@param pattern string A glob pattern
---@return Node[]
function Context:search(directory, pattern)use(directory) use(pattern) return {} end

---Runs a command. The returned object allows to capture the exit status and the output of the program.
---@param command_line (string|Node)[] The full command line to run.
---@return Process
function Context:popen(command_line)use(command_line) return Process end

---Logs a debug message. Debug messages are only printed in the console if the verbosity level is at least 2, but always
---appear in the log file.
---@param message string The message to log
function Context:debug(message)use(message) end

---Logs an info message. Info messages are only printed in the console if the verbosity level is at least 1, but always
---appear in the log file.
---@param message string The message to log
function Context:info(message)use(message) end

---Logs a warning message on the console and in the log file.
---@param message string The message to log
function Context:warn(message)use(message) end

---Logs an error message on the console and in the log file.
---@param message string The message to log
function Context:error(message)use(message) end

---Raises an error. This aborts the current call and unwinds until the previous `pcall` or `Context:try` call.
---@param message string The error message
function Context:fatal(message)use(message) end

---Runs a function in a try block, logging a message before and after the code has run.
---@param message string The message to print when beginning the operation
---@param func fun():any The code to run in the try block.
function Context:try(message, func)use(message)  use(func)  end

---Runs a function using a specific environment. The environment will be the default environment `context.env` while
---inside the function. After the function returns, the previous environment will be restored.
---@param env Environment the environment to use while in the function.
---@param func fun():any The code to run in the try block.
function Context:with(env, func)use(env) use(func) end

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
    use(name) use(fun) use(envs)
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
    use(name) use(fun)
    return depending
end
