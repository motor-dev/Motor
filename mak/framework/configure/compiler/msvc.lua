---@type(Context)
local context = ...

context:load_tool('compiler/msvc')

Bolt.MSVC.discover(function(env)
    return true
end, { ['c'] = {}, ['c++'] = { '/std:c++20' } }, {}, true)
