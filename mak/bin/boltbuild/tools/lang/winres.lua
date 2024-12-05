---@type Context
local context = ...
context:load_tool('internal/module_core')

context:command_driver('rc',
        'magenta',
        '${RC} ${RCFLAGS} ${RC_SRC_F:SRC[0]} ${RC_TGT_F:TGT[0]}')

Bolt.Winres = {}

function Bolt.Winres.find_winres(env)
    if not env.RC then
        context:try('Looking for rc', function()
            if env.COMPILER_NAME == 'msvc' then
                local rc = context:find_program('rc')
                env.RC = rc
                if rc then
                    env.RCFLAGS = { }
                    return rc
                else
                    context:raise_error('rc not found')
                end
            else
                env.RC = context:find_program(env.TRIPLE .. '-windres')
                if not env.RC then
                    env.RC = context:find_program(env.TARGET .. '-windres')
                end
                if not env.RC then
                    env.RC = context:find_program('windres')
                end
                if env.RC then
                    if env.LP64 then
                        env:append('RCFLAGS', { '-F', 'pe-x86-64' })
                    else
                        env:append('RCFLAGS', { '-F', 'pe-i386' })
                    end
                    env.RC_SRC_F = { '-i' }
                    env.RC_TGT_F = { '-o' }
                    return env.RC
                end
            end
        end)
    end
end

---@param generator Module
Bolt.ModuleCore.register_extension('ico', function(generator, source_file)
end)

---@param generator Module
Bolt.ModuleCore.register_extension('rc', function(generator, source_file)
    if generator.env.RC then
        local out_node = generator:make_build_node(source_file, 'obj')
        local task = generator:declare_task('rc', { source_file.full_path }, { out_node })
        table.insert(generator.compiled_tasks, task)
        table.insert(generator.objects, out_node)
    end
end)
