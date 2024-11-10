---@type Context
local context = ...

context.env.MOTOR_ARCHITECTURE = 'arm64'
context.env.MOTOR_ARCHITECTURES = { 'arm64', 'aarch64' }
context.env.MOTOR_ARCH_FAMILY = 'arm'
context.env.MOTOR_ARCH_LP64 = true
context.env:append('DEFINES', { '_ARM', '_ARM64', '_AARCH64', '_LP64' })