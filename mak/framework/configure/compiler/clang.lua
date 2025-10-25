---@type(Context)
local context = ...

context:load_tool('compiler/clang')

Bolt.Clang.discover(function(env)
    local target_os = env.TARGET_OS_VARIANT or env.TARGET_OS
    local version = env.CLANG_CXX_VERSION:gsub('-', '_')
    if env.CLANG_CXX_STDCPP_VERSION then
        version = version .. '+' .. env.CLANG_CXX_STDCPP_VERSION
    end
    env.TOOLCHAIN_ID = target_os .. '-' .. env.ARCHITECTURE .. '-' .. env.CXX_COMPILER_NAME .. '-' .. version
    env:append('CXXFLAGS', '-Wno-attributes')
    Motor.add_compiler(env)
    -- enumerate all
    return true
end, { ['c'] = {}, ['c++'] = { '--std=c++20' } }, {}, true)
