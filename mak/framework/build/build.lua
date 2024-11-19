---@type Context
local context = ...
context:load_tool('product')

local static, dynamic, nobulk = context.settings.static, context.settings.dynamic, context.settings.nobulk
context:declare_group(context.fs_name .. '.static', static and not nobulk)
context:declare_group(context.fs_name .. '.dynamic', dynamic and not nobulk)
context:declare_group(context.fs_name .. '.nobulk', not dynamic and not static and nobulk)
context:declare_group(context.fs_name .. '.static.nobulk', static and nobulk)
context:declare_group(context.fs_name .. '.dynamic.nobulk', dynamic and nobulk)
context:set_group_enabled(context.fs_name, not static and not dynamic and not nobulk)

Motor = { }

context:recurse('metagen.lua')
context:recurse('bulk.lua')
context:recurse('module/library.lua')
