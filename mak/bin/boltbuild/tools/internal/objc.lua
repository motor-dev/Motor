---@type Context
local context = ...

context:dependency_driver('objc', 'green', '${OBJC} ${OBJCFLAGS} ${OBJC_SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${OBJC_INCLUDE_ST:INCLUDES} ${OBJC_DEFINE_ST:DEFINES} ${C_SRC_FLAG:SRC} ${C_TGT_F:TGT[0]}')

context:load_tool('internal/module_core')
BoltModule.register_extension('m', function(generator, source_file)
    local out_node = generator:make_build_node(source_file, 'obj')
    local task = generator:declare_task('objc', { source_file.full_path }, { out_node })
    table.insert(generator.compiled_tasks, task)
    table.insert(generator.objects, out_node)
end)
