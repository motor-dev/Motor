---@type Context
local context = ...

context.motor_node = context.path
context:recurse('mak/framework/utils/string_ext.lua')
context:recurse('mak/framework/' .. context.fun)
context:recurse('src')

if context.fun == "init" then
    context.settings.flavors = {
        [1] = 'debug',
        [2] = 'profile',
        [3] = 'final',
    }
    context.settings.name = 'motor'
    context.settings.author = 'Motor <motor.devel@gmail.com>'
    context.settings.version = '0.1.0'
    context.settings.out = context.src_dir:make_node('build/.rswaf')
end
