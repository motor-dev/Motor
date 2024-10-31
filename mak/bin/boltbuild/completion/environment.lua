---@meta

local function use(var)
    return var
end

---Creates a new environment that inherits from the specified environment.
---@param env? Environment the base environment. If not specified, then derives the current environment.
---@return Environment a new Environment that inherits the values from env.
function Context:derive(env)
    return env
end

---Runs a function using a specific environment. The environment will become the default environment `context.env` while
---inside the function. After the function returns, the previous environment will be restored.
---@param env Environment the environment to use while in the function.
---@param func fun():any The code to run in the try block.
---@return any The return value of the delegate.
function Context:with(env, func)
    use(env)
    use(func)
end

---A container for some program-defined variables.
---Environments are stored across runs and can inherit from other environments. Additionally, values that are read from
---the environment are stored and will be used to verify if a stage is up-to-date.
---@class Environment
---@field [string] EnvironmentValue
Environment = {}

---A value stored in an environment.
---@alias EnvironmentValue nil|boolean|string|number|EnvironmentValue[]|Node
