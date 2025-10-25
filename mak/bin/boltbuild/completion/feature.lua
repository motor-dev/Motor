---@meta

--- Registers a callback function associated with a specific build feature or set of features.
--- - Features represent specific steps or capabilities within the build process, and each feature can have associated callbacks.
--- - This allows modular steps to be registered for execution when the given feature(s) are triggered.
---
---@param feature string|string[] A single feature or list of features that this callback is associated with.
---@param name string The name of this step, used for dependency management.
---@param callback fun(generator:Generator):void The function to execute when this feature is triggered.
---@return Feature #A new Feature object that allows setting dependency order.
function Context:feature(feature, name, callback)
end

--- Represents a feature in the build system, allowing configuration of its execution order in relation to other features.
---@class (exact) Feature
Feature = {}

--- Specifies steps that must be completed before this feature can execute.
--- - Attempts to set up a dependency cycle will cause an error, preventing any dependencies from being added.
---
---@param predecessors string[] An optional list of steps that must complete before this step runs.
---@return Feature #The same Feature object for chaining further configurations.
function Feature:set_run_after(predecessors)
end

--- Specifies steps that will run after this feature, making this step a prerequisite.
--- - Attempts to set up a dependency cycle will cause an error, preventing any dependencies from being added.
---
---@param successors string[] An optional list of steps that must execute after this step completes.
---@return Feature #The same Feature object for chaining further configurations.
function Feature:set_run_before(successors)
end

--- Posts a generator, triggering execution of all callbacks associated with the generator's features.
--- - Each registered feature callback for the generator is called in dependency order, potentially creating tasks or posting other generators.
--- - Posting the same generator multiple times has no additional effect.
---
---@param generator Generator The generator to post for execution.
function Context:post(generator)
end
