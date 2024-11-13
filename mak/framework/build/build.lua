---@type Context
local context = ...
context:load_tool('product')

Motor = { }

context:recurse('module/library.lua')
