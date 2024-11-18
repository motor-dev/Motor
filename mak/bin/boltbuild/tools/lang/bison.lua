---@type Context
local context = ...
context:load_tool('bolt')

Bolt.Bison = {}

function Bolt.Bison.find_bison()
    if not context.env.BISON then
        context:try('Looking for bison', function()
            local bison = context:find_program('bison')
            context.env.BISON = bison
            if bison then
                context.env.BISONFLAGS = { '-d' }
                return bison
            else
                error('bison not found')
            end
        end)
    end
end

context:command_driver('bison',
        'magenta',
        '${BISON} ${BISONFLAGS} ${SRC[0]} -o ${TGT[0]}',
        { 'c', 'cxx' })

context:extension('y,yy', function(generator, node, path)
    local out_node, directory = generator:make_build_node(node, path, 'src')
    local header
    if node:extension() == 'yy' then
        out_node = out_node:change_ext('cc')
        header = out_node:change_ext('hh')
    else
        out_node = out_node:change_ext('c')
        header = out_node:change_ext('h')
    end
    out_node.parent:mkdir()
    generator:declare_task('bison', { node }, { out_node, header })
    generator.source[1 + #generator.source] = { directory, out_node }
end)