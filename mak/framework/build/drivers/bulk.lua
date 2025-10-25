---@type Task
local task = ...

local content = ''
assert(#task.outputs == 1, 'Expected exactly one output for bulk include generation')
local source_dir = task.outputs[1].parent
local files = task.env.FILES
--- @cast files Node[]
for _, source in ipairs(files) do
    content = content .. '#include "' .. source:path_from(source_dir) .. '"\n'
end

task.outputs[1]:write(content)

return 0
