---@type Context
local context = ...

context:load_tool('compiler_core')

context:extension('cpp,cc,cxx,C', function(generator, node)
    local out_node = generator:make_build_node(node)
    local task = generator('cxx', { node }, { out_node })
    generator.compiled_tasks[1 + #generator.compiled_tasks] = task
    generator.objects[1 + #generator.objects] = out_node
end)

context:dependency_driver('cxx', 'green', '${CXX} ${CXXFLAGS} ${SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${INCLUDE_ST:INCLUDES} ${DEFINE_ST:DEFINES} ${CXX_SRC_FLAG:SRC} ${CXX_TGT_F:TGT[0]}')
