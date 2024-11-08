---@type Context
local context = ...

context.env.ARCHITECTURE = 'arm64'
context.env.VALID_ARCHITECTURES = { 'arm64', 'aarch64' }
context.env.ARCH_FAMILY = 'arm'
context.env.ARCH_LP64 = true
context.env:append('DEFINES', { '_ARM', '_ARM64', '_AARCH64', '_LP64' })