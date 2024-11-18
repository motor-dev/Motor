---@type Context
local context = ...

context:load_tool('lang/pkg_config')

if context.env.check_zlib then
    Bolt.pkg_config('motor.3rdparty.system.zlib', 'zlib')
end
if context.env.check_minizip then
    Bolt.pkg_config('motor.3rdparty.system.minizip', 'minizip')
end
