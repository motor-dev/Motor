local context = ...
context:try('setting up environment', function()
    return context.env.TOOLCHAIN_ID
end)
local target_name = context.env.TOOLCHAIN_ID
---@type string[]
local flavors = context.settings.flavors
for _, flavor in ipairs(flavors) do
    context:declare_command('build:' .. target_name .. ':' .. flavor, 'build', context.env)
end
