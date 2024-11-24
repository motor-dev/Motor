---@type Context
local context = ...

context:load_tool('tool/module')

if context.env.check_zlib then
    BoltModule.pkg_config('motor.3rdparty.system.zlib', 'zlib')
end
if context.env.check_minizip then
    BoltModule.pkg_config('motor.3rdparty.system.minizip', 'minizip')
end
