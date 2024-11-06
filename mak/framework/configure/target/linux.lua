---@type Context
local context = ...
local compilers = {}

for _, env in ipairs(Motor.compilers) do
    if env.TARGET:find('linux%-gnu') or env.TARGET:find('linux$') then
        compilers[1 + #compilers] = env
    end
end

if #compilers then
    context:colored_print(' {blue}configuring for platform Linux{reset}')
    for _, env in ipairs(compilers) do
        if Motor.test_compiler(env, '#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n') then
            context:try(' `- ' .. env.TOOLCHAIN_ID, function()
                Motor.create_toolchain(env)
                return 'OK'
            end)
        end
    end
end