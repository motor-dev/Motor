---@type Context
local context = ...

if context.fun == 'configure' then
elseif context.fun == 'build' then
    -- load build rules for C and C++
    context:load_tool('c')
    context:load_tool('cxx')
end