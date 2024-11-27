---@type Context
local context = ...

context:dependency_driver('cxx', 'green', '${CXX} ${CXXFLAGS} ${CXX_SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${CXX_INCLUDE_ST:INCLUDES} ${CXX_DEFINE_ST:DEFINES} ${CXX_SRC_F:SRC} ${CXX_TGT_F:TGT[0]}')

context:load_tool('internal/module_core')
BoltModule.register_extension('cpp,cc,cxx,C', function(generator, source_file)
    local out_node = generator:make_build_node(source_file, 'obj')
    local task = generator:declare_task('cxx', { source_file.full_path }, { out_node })
    table.insert(generator.compiled_tasks, task)
    table.insert(generator.objects, out_node)
end)