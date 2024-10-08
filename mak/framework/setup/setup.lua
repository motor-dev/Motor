local context = ...
local target_name = context.env.TARGET
---@type string[]
local flavors = context.settings.flavors
for _, flavor in ipairs(flavors) do
    context:declare_command('build:' .. target_name .. ':' .. flavor, 'build', context.env)
end
