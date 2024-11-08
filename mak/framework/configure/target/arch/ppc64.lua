---@type Context
local context = ...

context.env.ARCHITECTURE = 'ppc64'
context.env.VALID_ARCHITECTURES = { 'ppc64', 'powerpc64' }
context.env.ARCH_FAMILY = 'ppc'
context.env.ARCH_LP64 = true
context.env:append('DEFINES', { '_PPC', '_POWERPC', '_PPC64', '_POWERPC64', '_LP64' })
