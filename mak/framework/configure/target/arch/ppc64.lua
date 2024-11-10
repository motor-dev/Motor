---@type Context
local context = ...

context.env.MOTOR_ARCHITECTURE = 'ppc64'
context.env.MOTOR_ARCHITECTURES = { 'ppc64', 'powerpc64' }
context.env.MOTOR_ARCH_FAMILY = 'ppc'
context.env.MOTOR_ARCH_LP64 = true
context.env:append('DEFINES', { '_PPC', '_POWERPC', '_PPC64', '_POWERPC64', '_LP64' })
