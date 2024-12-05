---@type(Context)
local context = ...

context:load_tool('compiler/clang')

Bolt.Clang.discover(function(env)
    env.TOOLCHAIN_ID = env.TARGET_OS .. '-' .. env.ARCHITECTURE .. '-' .. env.CXX_COMPILER_NAME .. '-' .. env.CLANG_CXX_VERSION:gsub('-', '_')
    env:append('CXXFLAGS', '-Wno-attributes')
    Motor.add_compiler(env)
    -- enumerate all
    return true
end, { ['c'] = {}, ['c++'] = { '--std=c++20' } }, { }, true)
