---@meta

--- Represents a task generator, responsible for creating and managing tasks within the build system.
--- - Generators group tasks by name, feature, environment, and build group.
--- - Each generator has a default environment for its tasks, although specific tasks can use their own environments.
---@class Generator
---@field name string The name of the generator.
---@field path Node The path node associated with the generator. This is the context's current path at the moment the generator is declared.
---@field bld_dir Node The build directory node associated with the generator. This is a subdirectory of the context's build directory, named after the group and generator.
---@field group string The build group this generator belongs to. Groups can be shared across different build commands and must be declared using `context:declare_group`.
---@field env Environment The default environment. Tasks generated from this generator will inherit this environment unless another is specified.
---@field features string[] The list of features associated with this generator. Features are used to control the behavior of the generator and its tasks during the `post` phase.
local Generator

--- Declares a new group for organizing task generators, with conditional execution based on a specified condition.
--- - Groups are collections of task generators that allow for logical task organization and control over task execution.
--- - Each generator belongs to a group. By default, generators belong to the unnamed group, which is represented by the context's `fs_name` value and doesn’t require explicit declaration.
--- - Groups can be conditionally enabled or disabled based on a command-line option or a boolean value, which controls whether tasks within the group are scheduled for execution.
---
--- Conditional Execution:
--- - If `enabled_if` is a boolean, the group is enabled or disabled directly based on its value.
--- - If `enabled_if` is a string, it must refer to an existing command-line option, enabling the group based on the option's value at runtime.
---   Passing the option as a string bypasses the setting object, therefore avoiding an execution of the script in case the options change.
--- - When enabled, all tasks generated by the group's generators are scheduled for execution.
--- - When disabled, tasks in the group only run if required by dependencies of enabled tasks.
---
--- Shared Task Caching:
--- - Groups also support shared task caching across different commands.
--- - For example, tasks in a "preprocess" group can be reused across commands that share preprocessing needs, avoiding redundant execution.
--- - For efficient caching, tasks within the group must be declared consistently across commands to avoid cache conflicts and unnecessary recomputation.
---
---@param name string The unique name of the group.
---@param enabled_if boolean|string? A condition for enabling the group. If a boolean, it directly determines group status. If a string, it should refer to an existing command-line option, enabling the group based on the option's value. If no value is provided, the group is enabled unless other groups are enabled by command-line options.
function Context:declare_group(name, enabled_if)
end

--- Changes the enabling condition for an existing group.
--- - This method allows you to change the enabling condition for a group after it has been declared.
--- - The new condition can be a boolean value or a string referring to a command-line option, or even `nil` to set the group as default-enabled.
--- - default-enabled groups are always enabled unless other groups are enabled by command-line options.
---
--- @param name string The name of the group to enable or disable.
--- @param enabled boolean|string|nil A boolean value indicating whether the group should be enabled (`true`) or disabled (`false`).
function Context:set_group_enabled(name, enabled)
end

--- Sets the default group for the context.
--- - The default group is used when no specific group is specified for task generators.
---
--- @param name string The name of the group to set as the default.
function Context:set_default_group(name)
end

--- Creates a new task generator, associating it with a specified group for logical organization and caching.
--- - Generators are associated with groups to enable or disable their tasks collectively and to manage task caching.
--- - Groups can be conditionally enabled via `declare_group`, based on either boolean conditions or command-line options.
--- - If no group is specified, the generator will belong to the default group, which is represented by the context’s `fs_name` value.
---
---@param name string The name of the generator.
---@param features string|string[]? Initial list of features for this generator.
---@param env Environment? The default environment for tasks created by this generator.
---@param group string? The group this generator belongs to, declared via `declare_group` for conditional control. Defaults to the context’s `fs_name` value if not specified.
---@return Generator #A new generator object.
function Context:declare_generator(name, features, env, group)
end

--- Retrieves a generator by its name, if it exists.
---
---@param name string The name of the generator to search for.
---@return Generator|nil #The generator with the specified name, or `nil` if it is not found.
function Context:get_generator_by_name(name)
end

--- Posts a generator to initiate the execution of its associated feature callbacks.
--- - When posted, all methods linked to the generator's features are executed in dependency order.
--- - Callbacks may create additional tasks or post other generators. Posting the same generator multiple times has no effect.
---
---@param generator Generator The generator to post.
function Context:post(generator)
end

--- Creates a new task to transform specified inputs into outputs, using the given tool.
--- - Tasks represent build actions, with each one typically performing a specific transformation or build step.
--- - Inputs and outputs can be further adjusted after task creation.
---
---@param driver string The name of the driver used for the task (e.g., compiler, linker). The driver must have been declared in the context using one of `lua_driver`, `command_driver` or `dependency_driver`.
---@param inputs Node|Node[]? Initial inputs required for the task. Additional inputs can be added with `Task:add_input`.
---@param outputs Node|Node[]? Initial outputs produced by the task. Additional outputs can be added with `Task:add_output`.
---@param env Environment? The environment to use for this task, overriding the generator’s default environment if specified.
---@return Task #A new task object, ready for configuration and execution.
function Generator:declare_task(driver, inputs, outputs, env)
end

--- Checks if the generator has a specific property.
---
---@param name string The name of the property to check.
---@return boolean #`true` if the generator has a property with the specified name, otherwise returns `false`.
function Generator:has_property(name)
end
