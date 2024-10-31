---@type Context
local context = ...

context.motor_node = context.path

if context.fun == "init" then
    context.settings.flavors = {
        [1] = 'debug',
        [2] = 'profile',
        [3] = 'final',
    }
    context.settings.name = 'motor'
    context.settings.author = 'Motor <motor.devel@gmail.com>'
    context.settings.version = '0.1.0'
    context.settings.out = context.src_dir:make_node('build/.bolt')
    context.settings.tools_dir = {
        context.motor_node:make_node("mak/framework/tools"),
        context.motor_node:make_node("mak/framework/utils")
    }
end

context:load_tool('string_ext')
context:recurse('mak/framework/' .. context.fun)
context:recurse('src')
