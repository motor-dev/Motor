---@type Context
local context = ...

context.env.MOTOR_ARCHITECTURE = 'arm64eb'
context.env.MOTOR_ARCHITECTURES = { 'arm64eb', 'aarch64eb' }
context.env.MOTOR_ARCH_FAMILY = 'arm'
context.env.MOTOR_ARCH_LP64 = true
context.env:append('DEFINES', { '_ARM64EB', '_AARCH64EB', '_LP64' })