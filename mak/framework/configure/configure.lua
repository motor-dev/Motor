---@type Context
local context = ...

Motor = {
    compilers = {}
}

function Motor.add_compiler(env)
    Motor.compilers[1 + #Motor.compilers] = env
end

context.ARCHITECTURES = {
    --['x86'] = 'x86',
    --['i386'] = 'x86',
    --['i486'] = 'x86',
    --['i586'] = 'x86',
    --['i686'] = 'x86',
    ['amd64'] = 'amd64',
    ['x86_64'] = 'amd64',
    ['x64'] = 'amd64',
    --['arm'] = 'armv7a',
    --['armv6'] = 'armv6',
    --['armv7'] = 'armv7a',
    --['armv7a'] = 'armv7a',
    --['armv7s'] = 'armv7s',
    --['armv7k'] = 'armv7k',
    --['armv7l'] = 'armv7l',
    ['arm64'] = 'arm64',
    ['arm64e'] = 'arm64e',
    ['aarch64'] = 'arm64',
    --['aarch32'] = 'aarch32',
    --['arm64_32'] = 'arm64_32',
    --['aarch64_32'] = 'arm64_32',
    --['ppc'] = 'ppc',
    --['powerpc'] = 'ppc',
    ['ppc64'] = 'ppc64',
    ['powerpc64'] = 'ppc64',
    ['ppc64le'] = 'ppc64le',
    ['powerpc64le'] = 'ppc64le',
    ['ppu'] = 'ppu',
    ['spu'] = 'spu',
    --['ia64'] = 'ia64',
    --['itanium'] = 'ia64',
}

context:recurse('host/' .. context.settings.OS .. '.lua')

function context:create_toolchain()

    local target_name = platform.name .. '-' .. compiler.arch .. '-' .. compiler.name .. '-' .. compiler.version

    context:try(target_name, function()

        context:with(context:derive(), function()
            context.env.TARGET = target_name
            compiler.setup()
            platform.setup(compiler)

            local setup = context:declare_command('setup:' .. target_name, 'setup', context.env)
            local flavors = --[[---@type string[] ]] context.settings.flavors
            for _, flavor in ipairs(flavors) do
                context:chain_command(setup, 'build:' .. target_name .. ':' .. flavor, 'build')
            end
            if context.env.WITH_ASAN ~= nil then
                context:chain_command(setup, 'build:' .. target_name .. ':asan', 'build')
            end
            if context.env.WITH_TSAN ~= nil then
                context:chain_command(setup, 'build:' .. target_name .. ':tsan', 'build')
            end
            if context.env.WITH_UBSAN ~= nil then
                context:chain_command(setup, 'build:' .. target_name .. ':ubsan', 'build')
            end
        end)
    end)
end

local compilers = --[[---@type string[] ]] context.settings.compiler or { 'clang', 'gcc', 'msvc' }
local platforms = --[[---@type string[] ]] context.settings.platform or { 'linux', 'freebsd', 'macos', 'windows', 'solaris' }

for _, compiler in ipairs(compilers) do

    context:recurse('compiler/' .. compiler .. '.lua')
end

for _, platform in ipairs(platforms) do

    context:recurse('target/' .. platform .. '.lua')
end
