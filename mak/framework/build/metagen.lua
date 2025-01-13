---@type Context
local context = ...

context:declare_group('metagen', true)
context:lua_driver('metagen',
    'magenta',
    context.path:make_node('drivers/metagen.lua'),
    { 'c', 'cxx' })

pcall(function()
    context:popen({ context.env.PYTHON, context.path:make_node('../../lib/pyxx/__main__.py'), '-x', 'c++', '--std',
        'c++20', '-t', context.bld_dir:abs_path(), '-' })
end)

context:feature('metagen ', 'metagen ', function(generator)
    generator.out_namespace = {}
    for _, source_path in ipairs(generator.source) do
        for _, source_node in ipairs(context:search(source_path, '**/*.meta.hh')) do
            local target_node = context.bld_dir
            target_node = target_node:make_node(generator.group)
            target_node = target_node:make_node(generator.name)
            local target_node_src = target_node:make_node('src')
            local target_node_cc = target_node_src:make_node(source_node:path_from(source_path))
            target_node_cc = target_node_cc:change_ext('cc')
            local target_node_doc = target_node_cc:change_ext('doc')
            local target_node_ns = target_node_cc:change_ext('ns')

            local target_node_factory_hh_dir = target_node:make_node(source_path:name())
            local target_node_factory_hh = target_node_factory_hh_dir:make_node(source_node:path_from(source_path))
            target_node_factory_hh = target_node_factory_hh:change_ext('factory.hh')

            local task = generator:declare_task('metagen', { source_node },
                { target_node_cc, target_node_factory_hh, target_node_doc, target_node_ns })
            task.env.METAGEN_RELATIVE_INPUT = string.gsub(source_node:path_from(source_path), '\\', '/')
            task.env.METAGEN_RELATIVE_OUTPUT = string.gsub(target_node_factory_hh:path_from(target_node_factory_hh_dir),
                '\\', '/')
            task.env.METAGEN_ROOT_NAMESPACE = 'Motor'
            task.env.METAGEN_PLUGIN = 'motor'
            task.env.METAGEN_API = generator.api

            table.insert(generator.out_source, { target_node_src, target_node_cc })
            table.insert(generator.out_namespace, { target_node_src, target_node_ns })
        end
    end
end)

context:feature('module', 'process_out_source', function(generator)
    local metagen = context:get_generator_by_name(generator.name .. '.metagen')
    if metagen then
        ---@param source_node Node
        for _, source_node in ipairs(metagen.out_source) do
            generator:add_source(source_node[1], source_node[2])
        end
        return generator
    end
end):set_run_before({ 'process_source' })
