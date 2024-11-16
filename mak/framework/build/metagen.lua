---@type Context
local context = ...

context:declare_group('metagen', true)
context:command_driver('metagen',
        'magenta',
        '${PYTHON} ${METAGEN} -x c++ --std c++20 -D ${METAGEN_MACROS} --module ${METAGEN_PLUGIN} --root ${METAGEN_ROOT_NAMESPACE} --tmp ${METAGEN_TMP} ${SRC} ${METAGEN_RELATIVE_INPUT} ${METAGEN_RELATIVE_OUTPUT} ${TGT}',
        { 'c', 'cxx' })

context:feature('metagen', 'metagen', function(generator)
    for _, source_path in ipairs(generator.source) do
        for _, source_node in ipairs(context:search(source_path, '**/*.meta.hh')) do
            local target_node = context.bld_dir
            target_node = target_node:make_node(generator.group)
            target_node = target_node:make_node(generator.name)
            local target_node_src = target_node:make_node('src')
            local target_node_cc = target_node_src:make_node(source_node:path_from(source_path))
            target_node_cc = target_node_cc:change_ext('cc')
            local target_node_typeid_cc = target_node_cc:change_ext('typeid.cc')
            local target_node_doc = target_node_cc:change_ext('doc')
            local target_node_ns = target_node_cc:change_ext('ns')
            target_node_cc.parent:mkdir()

            local target_node_factory_hh_dir = target_node:make_node(source_path:name())
            local target_node_factory_hh = target_node_factory_hh_dir:make_node(source_node:path_from(source_path))
            target_node_factory_hh = target_node_factory_hh:change_ext('factory.hh')
            target_node_factory_hh.parent:mkdir()

            local task = generator('metagen', { source_node }, { target_node_cc, target_node_typeid_cc, target_node_factory_hh, target_node_doc, target_node_ns })
            task.env.METAGEN_RELATIVE_INPUT = source_node:path_from(source_path)
            task.env.METAGEN_RELATIVE_OUTPUT = target_node_factory_hh:path_from(target_node_factory_hh_dir)
            task.env.METAGEN_ROOT_NAMESPACE = 'Motor'
            task.env.METAGEN_PLUGIN = 'motor'
        end
    end
end)
