---@type Context
local context = ...

context:load_tool('compiler_core')

context:extension('cpp,cc,cxx,C', function(generator, node)
    local out_node = generator:make_build_node(node)
    local task = generator('cxx', { node }, { out_node })
    generator.compiled_tasks[1 + #generator.compiled_tasks] = task
end)
