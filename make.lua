local context = ...
context.env.motor_node = context.path
context:recurse('mak/framework/utils/string.lua')
context:recurse('mak/framework/' .. context.fun)
context:recurse('src')

if context.fun == "init" then
    context.settings.name = 'motor'
    context.settings.author = 'Motor <motor.devel@gmail.com>'
    context.settings.version = '0.1.0'
    context.settings.out = context.src_dir:make_node('build/.rswaf')
end
