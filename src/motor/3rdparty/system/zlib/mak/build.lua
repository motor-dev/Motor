---@type Context
local context = ...

context:load_tool('tool/module')

local zlib
if context.env.check_zlib then
    zlib = Bolt.Module.pkg_config('motor.3rdparty.system.zlib', 'zlib')
elseif context.env.ZLIB_SRC_NODE then
    local group = context.fs_name
    local lib_type = 'stlib'
    if context.settings.static then
        lib_type = 'stlib'
        group = group .. '.static'
    else
        group = group .. '.default'
    end
    if context.settings.nobulk then
        group = group .. '.nobulk'
    end

    zlib = Bolt.Module.module('motor.3rdparty.system.zlib', {
        group = group,
        features = { lib_type },
        source_patterns = {
            {path = context.env.ZLIB_SRC_NODE, pattern = '*.c'},
        },
        public_includes = {
            context.env.ZLIB_SRC_NODE,
        },

        internal_defines = { {'Z_HAVE_UNISTD_H', ''}, {'ZLIB_INTERNAL', ''} },
        public_defines = { {'ZLIB_DLL', ''} },
        flag_groups = { 'warn.none' },
    })
    zlib.nobulk = true
else
    context:raise_error('zlib not found')
end

if context.env.check_minizip then
    Bolt.Module.pkg_config('motor.3rdparty.system.minizip', 'minizip')
elseif context.env.MINIZIP_SRC_NODE then
    local group = context.fs_name
    local lib_type = 'stlib'
    if context.settings.static then
        lib_type = 'stlib'
        group = group .. '.static'
    else
        group = group .. '.default'
    end
    if context.settings.nobulk then
        group = group .. '.nobulk'
    end

    Bolt.Module.module('motor.3rdparty.system.minizip', {
        group = group,
        features = { lib_type },
        source = {
            { base_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip'),
              full_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip/ioapi.c') },
            { base_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip'),
              full_path = context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip/unzip.c') },
        },
        public_includes = {
            context.env.MINIZIP_SRC_NODE:make_node('contrib/minizip'),
        },
        public_defines = {
        },
        public_dependencies = {
            zlib
        },
        flag_groups = { 'warn.none' },
    })
else
    context:raise_error('minizip not found')
end
