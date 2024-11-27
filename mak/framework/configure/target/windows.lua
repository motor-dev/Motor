---@type Context
local context = ...
local compilers = {}

for _, env in ipairs(Motor.compilers) do
    if env.TARGET:find('mingw') or env.TARGET:find('windows') then
        table.insert(compilers, env)
    end
end

if #compilers then
    context:colored_print(' {blue}configuring for platform Windows{reset}')
    for _, env in ipairs(compilers) do
        context:with(env, function()
            if pcall(function()
                context:recurse('arch/' .. env.ARCHITECTURE .. '.lua')
            end) then
                if Motor.test_compiler(env, '#include <cstdio>\n#include <cfloat>\n#include <new>\nint main() {}\n') then
                    context:try(' `- ' .. env.TOOLCHAIN_ID, function()
                        context:load_tool('lang/winres')
                        BoltWinres.find_winres(env)
                        Motor.create_toolchain(env)
                        env:append('MOTOR_PLATFORMS', { 'windows', 'pc' })
                        env:append('DEFINES', 'MOTOR_PLATFORM=platform_windows')
                        if env.CXX_COMPILER_NAME == 'msvc' then
                            env:append('DEFINES', '_CRT_SECURE_NO_WARNINGS')
                        end
                        env:append('LIBS', { 'kernel32', 'user32', 'gdi32', 'winspool', 'comdlg32', 'advapi32', 'shell32', 'ole32', 'oleaut32', 'uuid', 'odbc32', 'odbccp32', 'synchronization' })
                        return 'OK'
                    end)
                end
            end
        end)
    end
end
