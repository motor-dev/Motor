---@type Context
local context = ...

if context.fun == 'configure' then
    if not context.env.CC then
        context.env.CC = context:find_program('clang')
    end
    if not context.env.CXX then
        context.env.CXX = context:find_program('clang')
    end
elseif context.fun == 'build' then
    -- load build rules for C and C++
    context:load_tool('c')
    context:load_tool('cxx')
end