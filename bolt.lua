---@type Context
local context = ...

context:recurse('mak/framework/' .. context.fun)
context:recurse('src')
