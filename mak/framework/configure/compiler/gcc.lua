---@type(Context)
local context = ...

context:load_tool('compilers/gcc')
for _, env in ipairs(Gcc.discover({}, { '--std=c++20' })) do
    local _, _, version = string.find(env.GCC_VERSION, '-(.*)')
    if version == nil then
        version = ''
    else
        version = '_' .. version
    end
    env.TOOLCHAIN_ID = env.TARGET_OS .. '-' .. env.ARCHITECTURE .. '-' .. env.CXX_COMPILER_NAME .. '-' .. env.GCC_CXX_VERSION:gsub('-', '_') .. version
    Motor.add_compiler(env)
end
