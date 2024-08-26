---@type Context
local context = ...

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

context.compilers = --[[---@type Compiler[] ]] {}

---@class Compiler
---@field name string
---@field target string
---@field arch string
---@field version string
---@field command string[]
---@field setup function():void
context.Compiler = {}
function context.Compiler:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    return o
end

---Runs the compiler, returns a success flag, the output and error log.
---@param command_line string[] Extra arguments to pass to the compiler
---@param input? string Optional input to pass to the compiler through standard input
function context.Compiler:run_cxx(command_line, input)
    local cl = {}
    for _, arg in ipairs(self.command_cxx) do
        cl[1+#cl] = arg
    end
    for _, arg in ipairs(command_line) do
        cl[1+#cl] = arg
    end
    return context:popen(cl):communicate(input)
end

---@class Platform
---@field name string
---@field setup function(compiler:Compiler):nil
context.Platform = {}
function context.Platform:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    return o
end

---@param compiler Compiler
---@param platform Platform
function context:create_toolchain(compiler, platform)
    local target_name = platform.name .. '-' .. compiler.arch .. '-' .. compiler.name .. '-' .. compiler.version

    context:try(target_name, function()

        context:with(context:derive(), function()
            context.env.TARGET = target_name


            local setup = context:declare_command('setup:' .. target_name, 'setup', context.env)
            local flavors = --[[---@type string[] ]] context.settings.flavors
            for _, flavor in ipairs(flavors) do
                context:chain_command(setup, 'build:' .. target_name .. ':' .. flavor, 'build')
            end
        end)
        compiler.setup()
        platform.setup(compiler)
    end)
end

local compilers = --[[---@type string[] ]] context.settings.compiler or { 'clang', 'gcc', 'msvc', 'suncc' }
local platforms = --[[---@type string[] ]] context.settings.platform or { 'linux', 'freebsd', 'macos', 'windows', 'solaris' }
for _, compiler in ipairs(compilers) do
    context:recurse('compiler/' .. compiler .. '.lua')
end

for _, platform in ipairs(platforms) do
    context:recurse('target/' .. platform .. '.lua')
end
