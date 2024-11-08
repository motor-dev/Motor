---@type Context
local context = ...
context:load_tool('compiler_module')

Motor = { }

context:recurse('module/library.lua')
