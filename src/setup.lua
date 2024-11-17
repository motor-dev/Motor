---@type Context
local context = ...

for _, node in ipairs(context:search(context.path, 'motor/3rdparty/**/mak/setup.lua')) do
    context:recurse(node:path_from(context.path))
end