---@type Context
local context = ...
context:load_tool('internal/module_core')

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
                context:raise_error('bison not found')
            end
        end)
    end
end

context:command_driver('bison',
        'magenta',
        '${BISON} ${BISONFLAGS} ${SRC[0]} -o ${TGT[0]}',
        { 'c', 'cxx' })

---@param generator Module
Bolt.ModuleCore.register_extension('y,yy', function(generator, source_file)
    local out_node, directory = generator:make_build_node(source_file, 'src')
    local header
    if source_file.full_path:extension() == 'yy' then
        out_node = out_node:change_ext('cc')
        header = out_node:change_ext('hh')
    else
        out_node = out_node:change_ext('c')
        header = out_node:change_ext('h')
    end
    generator:declare_task('bison', { source_file.full_path }, { out_node, header })
    generator:add_source(directory, out_node)
end)