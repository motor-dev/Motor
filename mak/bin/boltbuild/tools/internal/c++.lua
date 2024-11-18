---@type Context
local context = ...

context:dependency_driver('cxx', 'green', '${CXX} ${CXXFLAGS} ${CXX_SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${CXX_INCLUDE_ST:INCLUDES} ${CXX_DEFINE_ST:DEFINES} ${CXX_SRC_FLAG:SRC} ${CXX_TGT_F:TGT[0]}')

context:load_tool('internal/product_core')
context:extension('cpp,cc,cxx,C', function(generator, node, path)
    local out_node = generator:make_build_node(node, path)
    out_node.parent:mkdir()
    local task = generator:declare_task('cxx', { node }, { out_node })
    generator.compiled_tasks[1 + #generator.compiled_tasks] = task
    generator.objects[1 + #generator.objects] = out_node
end)