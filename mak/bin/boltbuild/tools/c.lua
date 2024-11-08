---@type Context
local context = ...

context:load_tool('compiler_core')

context:extension('c', function(generator, node)
    local out_node = generator:make_build_node(node)
    local task = generator('c', { node }, { out_node })
    generator.compiled_tasks[1 + #generator.compiled_tasks] = task
    generator.objects[1 + #generator.objects] = out_node
end)

context:dependency_driver('c', 'green', '${CC} ${CFLAGS} ${SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${INCLUDE_ST:INCLUDES} ${DEFINE_ST:DEFINES} ${CC_SRC_FLAG:SRC} ${CC_TGT_F:TGT[0]}')
