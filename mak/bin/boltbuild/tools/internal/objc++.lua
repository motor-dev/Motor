---@type Context
local context = ...

context:dependency_driver('objcxx', 'green', '${OBJCXX} ${OBJCXXFLAGS} ${OBJCXX_SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${OBJCXX_INCLUDE_ST:INCLUDES} ${OBJCXX_DEFINE_ST:DEFINES} ${OBJCXX_SRC_FLAG:SRC} ${OBJCXX_TGT_F:TGT[0]}')

context:load_tool('internal/module_core')
BoltModule.register_extension('mm', function(generator, source_file)
    local out_node = generator:make_build_node(source_file, 'obj')
    local task = generator:declare_task('objcxx', { source_file.full_path }, { out_node })
    table.insert(generator.compiled_tasks, task)
    table.insert(generator.objects, out_node)
end)