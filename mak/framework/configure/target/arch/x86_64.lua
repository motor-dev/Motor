---@type Context
local context = ...

context.env.ARCHITECTURE = 'x86_64'
context.env.VALID_ARCHITECTURES = { 'amd64', 'x64', 'x86_64' }
context.env.ARCH_FAMILY = 'x86'
context.env.ARCH_LP64 = true
context.env:append('DEFINES', { '_AMD64', '_LP64' })
