---@type Context
local context = ...

context:dependency_driver('c', 'green', '${CC} ${CFLAGS} ${C_SYSTEM_INCLUDE_ST:SYSTEM_INCLUDES} ${C_INCLUDE_ST:INCLUDES} ${C_DEFINE_ST:DEFINES} ${C_SRC_F:SRC} ${C_TGT_F:TGT[0]}')

context:load_tool('internal/module_core')
Bolt.Module.register_extension('c', function(generator, source_file)
    local out_node = generator:make_build_node(source_file, 'obj')
    local task = generator:declare_task('c', { source_file.full_path }, { out_node })
    table.insert(generator.compiled_tasks, task)
    table.insert(generator.objects, out_node)
end)
