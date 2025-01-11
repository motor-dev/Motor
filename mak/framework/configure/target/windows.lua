---@type Context
local context = ...
local compilers = {}

for _, env in ipairs(Motor.compilers) do
    if env.TARGET_OS == 'windows' then
        table.insert(compilers, env)
    end
end

if #compilers then
    context:colored_println(' {blue}configuring for platform Windows{reset}')
    for _, env in ipairs(compilers) do
        context:with(env, function()
            if pcall(function()
                context:recurse('arch/' .. env.ARCHITECTURE .. '.lua')
            end) then
                if Motor.test_compiler(env, '#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n') then
                    context:try(' `- ' .. env.TOOLCHAIN_ID, function()
                        context:load_tool('lang/winres')
                        Bolt.Winres.find_winres(env)
                        Motor.create_toolchain(env)
                        env:append('MOTOR_PLATFORMS', { 'windows', 'pc' })
                        env:append('DEFINES', 'MOTOR_PLATFORM=platform_windows')
                        if env.CXX_COMPILER_NAME == 'msvc' then
                            env:append('DEFINES', '_CRT_SECURE_NO_WARNINGS')
                        end
                        env:append('SYSTEM_INCLUDES', context.env.motor_node:make_node('src/motor/3rdparty/system/win32/api.windows'):abs_path())
                        env:append('LIBS', { 'kernel32', 'user32', 'advapi32', 'ole32', 'oleaut32', 'uuid', 'shell32', 'synchronization' })
                        return 'OK'
                    end)
                end
            end
        end)
    end
end
