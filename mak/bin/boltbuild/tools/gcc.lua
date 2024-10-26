---@type Context
local context = ...

-- load build rules for C and C++
context:load_tool('c')
context:load_tool('cxx')
