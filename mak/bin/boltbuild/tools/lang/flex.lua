---@type Context
local context = ...
context:load_tool('internal/module_core')

BoltFlex = {}

function BoltFlex.find_flex()
    if not context.env.FLEX then
        context:try('Looking for flex', function()
            local flex = context:find_program('flex')
            context.env.FLEX = flex
            if flex then
                context.env.FLEXFLAGS = { }
                return flex
            else
                context:raise_error('flex not found')
            end
        end)
    end
end

context:command_driver('flex',
        'magenta',
        '${FLEX} ${FLEXFLAGS} -o ${TGT[0]} ${SRC[0]}',
        { 'c', 'cxx' })

---@param generator Module
BoltModule.register_extension('l,ll', function(generator, source_file)
    local out_node, directory = generator:make_build_node(source_file, 'src')
    if source_file.full_path:extension() == 'll' then
        out_node = out_node:change_ext('cc')
    else
        out_node = out_node:change_ext('c')
    end
    generator:declare_task('flex', { source_file.full_path }, { out_node })
    generator:add_source(directory, out_node)
end)