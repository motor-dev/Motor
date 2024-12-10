---@type Context
local context = ...
context:load_tool('tool/module')

local static, dynamic, nobulk = context.settings.static, context.settings.dynamic, context.settings.nobulk

local group_name = context.fs_name
if static then
    group_name = group_name .. '.static'
elseif dynamic then
    group_name = group_name .. '.dynamic'
else
    group_name = group_name .. '.default'
end

if nobulk then
    group_name = group_name .. '.nobulk'
end
context:declare_group(group_name, true)
context:set_default_group(group_name)

Motor = { }

context:recurse('metagen.lua')
context:recurse('bulk.lua')
context:recurse('module/library.lua')
