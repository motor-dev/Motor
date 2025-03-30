---@meta

--- Creates a new, empty `Environment` instance.
--- This function initializes and returns a new `Environment` object, which can be used to store and manage
--- environment variables and their values. The new environment is empty and does not inherit any values
--- from other environments.
---
---@return Environment #A new, empty `Environment` instance.
function Context:new_env()
end

--- Creates a new environment that inherits values from the specified base environment.
--- The derived environment maintains a dynamic link to the base environment, so any values set in the base environment
--- after the derivation will still be accessible in the derived environment, unless they are shadowed by values
--- set directly in the derived environment.
--- This allows the derived environment to stay updated with changes to the base environment, while also allowing
--- customizations specific to the derived environment.
---
---@param env Environment? The base environment to inherit from. If not provided, defaults to the current environment.
---@return Environment #A new `Environment` instance with inherited values from `env`.
function Context:derive(env)
end

--- Temporarily sets the specified environment as the active `context.env` for the duration of a function's execution.
--- This allows a command to run with an isolated environment that will automatically revert once the function completes,
--- even if an error is raised. If `func` raises an error, `Context:with` will properly restore the previous environment
--- before propagating the error.
---
---@param env Environment The environment to set as `context.env` during the function's execution.
---@param func fun():any The function to execute with `env` as the active environment.
---@return any #The return value of the function executed in the specified environment.
function Context:with(env, func)
end

--- Represents a collection of key-value pairs stored across runs and used to share configuration data between commands.
--- Environments can inherit values from other environments and are passed to sub-commands as needed.
--- Commands may modify their environment and declare sub-commands that utilize these values (e.g., `configure` might set
--- environment variables that the `build` command then uses).
--- Additionally, environments track values that are read during execution to check if a stage is up-to-date on subsequent runs.
---@class Environment
---@field [string] EnvironmentValue A dynamic key-value storage for environment variables.
Environment = {}

--- Appends a value or an array of values to an environment variable.
--- - If the variable already exists and is an array, the new element(s) are appended to the existing array.
--- - If the variable already exists and is not an array, the value is turned into an array with the existing value as the first element, and the new elements are appended.
--- - If the variable does not exist, it is created as an array with the new element(s).
---
---@param var_name string The name of the environment variable.
---@param value EnvironmentValue The value(s) to append to the environment variable.
function Environment:append(var_name, value)
end

--- A value type that can be stored within an environment. Supported types include `nil`, `boolean`, `string`, `number`,
--- arrays of `EnvironmentValue`, `Node` references and references to other `Environment` instances.
---@alias EnvironmentValue (nil|boolean|string|number|Node|Environment|(nil|boolean|string|number|Node|Environment)[])
