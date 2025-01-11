---@type(Context)
local context = ...

context:load_tool('compiler/msvc')

Bolt.MSVC.discover(function(env)
    env.TOOLCHAIN_ID = env.TARGET_OS .. '-' .. env.ARCHITECTURE .. '-' .. env.CXX_COMPILER_NAME .. '-' .. env.CL_VERSION
    Motor.add_compiler(env)
    return true
end, { ['c'] = {}, ['c++'] = { '/std:c++20' } }, {}, true)
