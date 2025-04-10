---@type Context
local context = ...

context:load_tool('tool/module')

local zlib
if context.env.check_zlib then
    zlib = Bolt.Module.pkg_config('motor.3rdparty.system.zlib', 'zlib')
elseif context.env.ZLIB_SRC_NODE then
    local lib_type
    local defines = {}
    if context.settings.static then
        lib_type = 'stlib'
    else
        lib_type = 'shlib'
        defines[1] = { 'ZLIB_DLL', '' }
    end

    ---@type ModuleProperties
    local properties = {
        features = { lib_type },
        source_patterns = {
            [1] = --[[@type SourcePattern ]] { path = context.env.ZLIB_SRC_NODE, pattern = '*.c' },
        },
        public_includes = { [1] = --[[@type Node]] context.env.ZLIB_SRC_NODE, },

        internal_defines = { { 'Z_HAVE_UNISTD_H', '' }, { 'ZLIB_INTERNAL', '' } },
        public_defines = defines,
        flag_groups = { 'warn.none' },
    }
    zlib = Bolt.Module.module('motor.3rdparty.system.zlib', properties)
    zlib.nobulk = true
else
    context:raise_error('zlib not found')
end

if context.env.check_minizip then
    Bolt.Module.pkg_config('motor.3rdparty.system.minizip', 'minizip')
elseif context.env.MINIZIP_SRC_NODE then
    local lib_type
    local defines = {}
    if context.settings.static then
        lib_type = 'stlib'
    else
        lib_type = 'shlib'
        defines[1] = { 'ZLIB_DLL', '' }
    end

    Bolt.Module.module('motor.3rdparty.system.minizip', {
        features = { lib_type },
        source = {
            {
                base_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip'),
                full_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip/ioapi.c')
            },
            {
                base_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip'),
                full_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip/unzip.c')
            },
        },
        internal_defines = { { 'Z_HAVE_UNISTD_H', '' }, { 'ZLIB_INTERNAL', '' } },
        public_includes = {
            context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip'),
        },
        public_defines = defines,
        public_dependencies = {
            zlib
        },
        flag_groups = { 'warn.none' },
    })
else
    context:raise_error('minizip not found')
end
