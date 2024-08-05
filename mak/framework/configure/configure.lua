local context = ...

context.ARCHS = {
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
context.compilers = {}

for _, compiler in ipairs(context.settings.compiler or { 'clang', 'gcc', 'msvc', 'suncc' }) do
    context:recurse('compiler/' .. compiler .. '.lua')
end

for _, platform in ipairs(context.settings.platform or { 'linux', 'freebsd', 'macos', 'windows', 'solaris' }) do
    context:recurse('target/' .. platform .. '.lua')
end