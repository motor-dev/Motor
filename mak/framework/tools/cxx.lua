---@type Context
local context = ...

context:load_tool('compiler_core')

context:extension('cxx', function(task_gen, node)
    print('hop')
end)