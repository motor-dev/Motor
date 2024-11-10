---@type Context
local context = ...

context.env.MOTOR_ARCHITECTURE = 'x86_64'
context.env.MOTOR_ARCHITECTURES = { 'amd64', 'x64', 'x86_64' }
context.env.MOTOR_ARCH_FAMILY = 'x86'
context.env.MOTOR_ARCH_LP64 = true
context.env:append('DEFINES', { '_AMD64', '_LP64' })
