---@type(Context)
local context = ...

context:load_tool('compiler/gcc')

Bolt.GCC.discover(function(env)
    ---@type string
    local gcc_version = env.GCC_VERSION
    local _, _, version = string.find(gcc_version, '-(.*)')
    if version == nil then
        version = ''
    else
        version = '_' .. version
    end
    env.TOOLCHAIN_ID = env.TARGET_OS ..
    '-' .. env.ARCHITECTURE .. '-' .. env.CXX_COMPILER_NAME .. '-' .. env.GCC_CXX_VERSION:gsub('-', '_') .. version
    env:append('CXXFLAGS', '-Wno-attributes')
    Motor.add_compiler(env)
    return true
end, { ['c'] = {}, ['c++'] = { '--std=c++20' } }, {}, true)
