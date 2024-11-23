---@type Context
local context = ...
context:load_tool('bolt')
context:load_tool('internal/product_core')

Bolt.Flex = {}

function Bolt.Flex.find_flex()
    if not context.env.FLEX then
        context:try('Looking for flex', function()
            local flex = context:find_program('flex')
            context.env.FLEX = flex
            if flex then
                context.env.FLEXFLAGS = { }
                return flex
            else
                error('flex not found')
            end
        end)
    end
end

context:command_driver('flex',
        'magenta',
        '${FLEX} ${FLEXFLAGS} -o ${TGT[0]} ${SRC[0]}',
        { 'c', 'cxx' })

context:extension('l,ll', function(generator, node, path)
    local out_node, directory = generator:make_build_node(node, path, 'src')
    if node:extension() == 'll' then
        out_node = out_node:change_ext('cc')
    else
        out_node = out_node:change_ext('c')
    end
    generator:declare_task('flex', { node }, { out_node })
    table.insert(generator.source, { directory, out_node })
end)