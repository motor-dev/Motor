---@type Context
local context = ...
context:load_tool('product')

Motor = { }

context:recurse('metagen.lua')
context:recurse('module/library.lua')
