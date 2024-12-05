---@type Context
local context = ...

context:load_tool('tool/pkg_config')
context:load_tool('tool/patch')
local ZLIB_SOURCES = 'https://zlib.net/fossils/zlib-1.2.12.tar.gz'
local ZLIB_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/zlib-1.2.11-%(platform)-%(arch)-%(abi).tgz'
local MINIZIP_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/minizip-1.2.11-%(platform)-%(arch)-%(abi).tgz'


local function unpack_zlib()
    context:declare_group('zlib_src', true)
    g = context:declare_generator('zlib_src', {}, context.env, 'zlib_src')
    local out_node = context.bld_dir:make_node('zlib_src/download/zlib-1.2.12.tar.gz')
    g:declare_task('wget', { }, { out_node }).env.WGET_URL = ZLIB_SOURCES
    local unpack_node = context.bld_dir:make_node('zlib_src/archive')
    local src_node = context.bld_dir:make_node('zlib_src/src')
    local patches = context:search(g.path.parent:make_node('patches'), '*')
    g:declare_task('untar', { out_node }, { unpack_node })
    Bolt.Patch.patch(g, patches, unpack_node:make_node('zlib-1.2.12'), src_node)
    return src_node
end

local function setup_zlib_pkg_config()
    return pcall(function()
        Bolt.PkgConfig.pkg_config('zlib', 'zlib')
    end)
end

local function setup_zlib_system()
    return false
end

local function setup_zlib_prebuilt()
    return false
end

local function setup_zlib_source()
    if Bolt.Wget.check(ZLIB_SOURCES) then
        context.env.ZLIB_SRC_NODE = unpack_zlib()
        return true
    end
    
    return false
end

context:try('  zlib', function()
    local option = context.settings.with_zlib
    if option == 'best' or option == 'pkgconfig' then
        if setup_zlib_pkg_config() then
            return 'from pkg-config'
        end
    end
    if option == 'best' or option == 'system' then
        if setup_zlib_system() then
            return 'from system'
        end
    end
    if option == 'best' or option == 'prebuilt' then
        if setup_zlib_prebuilt() then
            return 'from prebuilt'
        end
    end
    if option == 'best' or option == 'source' then
        if setup_zlib_source() then
            return 'from source'
        end
    end
    context:raise_error('not found')
end)

local function setup_minizip_pkg_config()
    return pcall(function()
        Bolt.PkgConfig.pkg_config('minizip', 'minizip')
    end)
end

local function setup_minizip_system()
    return false
end

local function setup_minizip_prebuilt()
    return false
end

local function setup_minizip_source()
    if context.env.ZLIB_SRC_NODE then
        context.env.MINIZIP_SRC_NODE = context.env.ZLIB_SRC_NODE
        return true
    end
    if Bolt.Wget.check(ZLIB_SOURCES) then
        context.env.MINIZIP_SRC_NODE = unpack_zlib()
        return true
    end
    return false
end

context:try('  minizip', function()
    local option = context.settings.with_minizip
    if option == 'best' or option == 'pkgconfig' then
        if setup_minizip_pkg_config() then
            return 'from pkg-config'
        end
    end
    if option == 'best' or option == 'system' then
        if setup_minizip_system() then
            return 'from system'
        end
    end
    if option == 'best' or option == 'prebuilt' then
        if setup_minizip_prebuilt() then
            return 'from prebuilt'
        end
    end
    if option == 'best' or option == 'source' then
        if setup_minizip_source() then
            return 'from source'
        end
    end
    context:raise_error('not found')
end)