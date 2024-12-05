---@type Context
local context = ...
context:load_tool("internal/bolt")

Bolt.Copy = {}

--- @param generator Generator The generator object that declares the task.
--- @param source Node
--- @param destination Node
--- @return Node The target node of the copy task.
function Bolt.Copy.copy(generator, source, destination)
    local destination = destination:make_node(source:name())
    generator:declare_task('copy', { source }, { destination })
    return destination
end
