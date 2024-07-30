local context = ...
context.env.motor_node = context.path
context:recurse('mak/framework/' .. context.fun)
context:recurse('src')

if context.stage == "init" then
    context.settings.name = 'motor'
    context.settings.author = 'Motor <motor.devel@gmail.com>'
    context.settings.version = '0.1.0'
    context.settings.out = context.srcdir:make_node('build/.rswaf')
end
