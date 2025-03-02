---@type Task
local task = ...

local content = ''
local source_dir = task.outputs[1].parent
--- @type Node[]
local files = task.env.FILES
for _, source in ipairs(files) do
    content = content .. '#include "' .. source:path_from(source_dir) .. '"\n'
end

task.outputs[1]:write(content)

return 0
