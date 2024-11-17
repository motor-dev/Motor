---@type Context
local context = ...

context:declare_group('metagen', true)
context:command_driver('metagen',
        'magenta',
        '${PYTHON} ${METAGEN} -x c++ --std c++20 -D ${METAGEN_MACROS} --module ${METAGEN_PLUGIN} --root ${METAGEN_ROOT_NAMESPACE} --tmp ${METAGEN_TMP} ${SRC} ${METAGEN_RELATIVE_INPUT} ${METAGEN_RELATIVE_OUTPUT} ${TGT}',
        { 'c', 'cxx' })

pcall(function()
    context:popen(context.env.PYTHON:abspath() .. ' ' .. context.path:make_node('../../lib/pyxx/__main__.py'):abspath() .. ' -x c++ -t ' .. context.bld_dir:abs_path() .. ' -')
end)

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

            generator.out_source[1 + #generator.out_source] = { target_node_src, target_node_cc }
            generator.out_source[1 + #generator.out_source] = { target_node_src, target_node_typeid_cc }
        end
    end
end)

context:feature('c,cxx', 'process_out_source', function(generator)
    local metagen = context:get_generator_by_name(generator.name .. '.metagen')
    ---@param source_node Node
    for _, source_node in ipairs(metagen.out_source) do
        generator:add_source(source_node[1], source_node[2])
    end
    return generator
end)   :set_run_before({ 'process_source' })