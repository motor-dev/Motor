---@type Context
local context = ...

context.env.ARCHITECTURE = 'ppc64le'
context.env.VALID_ARCHITECTURES = { 'ppc64le', 'powerpc64le' }
context.env.ARCH_FAMILY = 'ppc'
context.env.ARCH_LP64 = true
context.env:append('DEFINES', { '_PPC', '_POWERPC', '_PPC64', '_POWERPC64', '_PPC64LE', '_POWERPC64LE', '_LP64' })
