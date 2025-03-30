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
context:declare_group(group_name, not context.env.PROJECTS)
context:set_default_group(group_name)

Motor = {}

context:recurse('metagen.lua')
context:recurse('bulk.lua')
context:recurse('module/library.lua')


context:recurse('projects/cmake.lua')
context:recurse('projects/clion.lua')
context:recurse('projects/qtcreator.lua')
context:recurse('projects/visual_studio.lua')
context:recurse('projects/vscode.lua')
context:recurse('projects/xcode.lua')
