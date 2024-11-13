---@type Context
local context = ...

context:dependency_driver('c', 'green', '${CC} ${CFLAGS} ${CC_SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${CC_INCLUDE_ST:INCLUDES} ${CC_DEFINE_ST:DEFINES} ${CC_SRC_FLAG:SRC} ${CC_TGT_F:TGT[0]}')

context:load_tool('internal/product_core')
context:extension('c', function(generator, node, path)
    local out_node = generator:make_build_node(node, path)
    out_node.parent:mkdir()
    local task = generator('c', { node }, { out_node })
    generator.compiled_tasks[1 + #generator.compiled_tasks] = task
    generator.objects[1 + #generator.objects] = out_node
end)
