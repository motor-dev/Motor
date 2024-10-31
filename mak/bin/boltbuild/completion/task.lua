---@meta

local function use(var)
    return var
end

---@class Task
---@field name string The name of the driver that will execute the task.
---@field generator string The name of the generator that created the task.
---@field group string The name of the group of the generator.
---@field env Environment The environment, derived from the generator's environment.
---@field inputs Node[] The nodes this task will use as inputs.
---@field outputs Node[] The nodes produced by this task.
Task = {}

---Add a node or a list of nodes to the declared input of this task. This will also adjust task depenencies.
---This function will fail if adding one of the nodes creates a cycle in the task dependency graph. In this
---case, the function will not add any input to the list and raise an error instead.
---@param input Node|Node[] A node or a list of nodes that this task will use as inputs
function Task:add_input(input)
    use(input)
end

---Add a node or a list of nodes to the declared output of this task. This will also adjust task depenencies.
---This function will fail if adding one of the nodes creates a cycle in the task dependency graph. In this
---case, the function will not add any output to the list and raise an error instead.
---@param output Node|Node[] A node or a list of nodes that this task will create.
function Task:add_output(output)
    use(output)
end