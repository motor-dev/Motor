---@meta

--- Recursively loads or executes the script at the specified `path`.
--- - If `path` is a file, it will be executed directly.
--- - If `path` is a directory, the function will search for a file named after the `context.fun` basename in that directory
---   (e.g., if `context.fun` is `"build"`, it will look for `build.lua`).
---
---@param path string The path to the file or directory, either absolute or relative to the context's current path.
function Context:recurse(path)
end

--- Loads a tool file to add specific functionality to the build context.
--- Tools provide reusable commands or settings and can be automatically loaded by dependent commands when needed.
--- - If the tool is already loaded, it will not reload by default unless `reload` is set to `true`.
--- - The function searches for `tool_name.lua` within directories specified in the `tools_dir` setting.
---
---@param tool_name string The name of the tool file to load (without the `.lua` extension).
---@param reload boolean? Optional. If `true`, reloads the tool even if it has already been loaded. Defaults to `false`.
function Context:load_tool(tool_name, reload)
end

--- Represents a command that has been declared within the context.
--- Commands correspond to distinct build steps (like "configure" or "build") and must be declared before they can be executed.
--- Command declarations may include chaining, allowing commands to declare additional commands upon execution.
---@class DeclaredCommand
local DeclaredCommand = {}

--- Declares a new build command.
--- Each command represents a distinct build action (such as "configure" or "build") and must have a unique name.
--- Declared commands can inherit one or more environments, which will provide configuration and context for the command.
---
---@param name string The unique name of the command to declare. This name is linked to `Context.name`.
---@param fun string The function name associated with this command, linked to `Context.fun`.
---@param envs Environment|Environment[]? An environment or list of environments that this command will use.
---   Derived environments will inherit from these environments for use during command execution.
---@return DeclaredCommand #A `DeclaredCommand` object representing the newly declared command, which can be used for chaining.
function Context:declare_command(name, fun, envs)
end

--- Declares a command that will be formally declared by another command upon its execution.
--- This setup allows commands to define other commands that depend on them, forming a command chain.
--- If a dependent command is run before its prerequisite command, the prerequisite will be run first.
---
---@param depending DeclaredCommand The command that must be executed before this new command is formally declared.
---@param name string The unique name of the new command. Each command must have a unique name. Linked to `Context.name`.
---@param fun string The function name associated with the new command, corresponding to `Context.fun`.
---@return DeclaredCommand #A `DeclaredCommand` object for the newly declared chained command, allowing further declarations if needed.
function Context:chain_command(depending, name, fun)
end
