---@meta

---A container for some program-defined variables.
---
---Environments are stored across runs and can inherit from other environments. Additionally, values that are read from
---the environment are stored and will be used to verify if a stage is up-to-date.
---@class Environment
---@field [string] EnvironmentValue
Environment = {}

---A value stored in an environment.
---@alias EnvironmentValue nil|boolean|string|number|EnvironmentValue[]|Node
