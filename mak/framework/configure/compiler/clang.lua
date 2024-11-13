---@type(Context)
local context = ...

context:load_tool('compilers/clang')
for _, env in ipairs(Clang.discover({}, { '--std=c++20' })) do
    env.TOOLCHAIN_ID = env.TARGET_OS .. '-' .. env.ARCHITECTURE .. '-' .. env.CXX_COMPILER_NAME .. '-' .. env.CLANG_CXX_VERSION:gsub('-', '_')
    Motor.add_compiler(env)
end
