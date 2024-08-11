---@type Context
context = ...

for _, --[[---@type std__Packed<string>]] tool_table in ipairs(context.compilers) do
    local tool, compiler, architecture, target, version, includes, defines = table.unpack(tool_table)
    if target:find('%-linux%-gnu') then
        context:with(context:derive(context.env), function()
            local target_name = 'linux-' .. architecture .. '-' .. tool .. '-' .. version[1] .. '.' .. version[2] .. '.' .. version[3]
            context.env.TARGET = target_name
            local setup = context:declare_command('setup:' .. target_name, 'setup', context.env)
            ---@type string[]
            local flavors = context.settings.flavors
            for _, flavor in ipairs(flavors) do
                context:chain_command(setup, 'build:' .. target_name .. ':' .. flavor, 'build')
            end
        end)
    end
end