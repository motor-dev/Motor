---@type Context
local context = ...

if context.fun == 'configure' then
end
-- load build rules for C and C++
context:load_tool('c')
context:load_tool('cxx')
