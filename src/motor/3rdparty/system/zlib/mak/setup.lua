---@type Context
local context = ...

context:load_tool('tool/pkg_config')

local function setup_zlib_pkg_config()
    return pcall(function()
        BoltPkgConfig.pkg_config('zlib', 'zlib')
    end)
end

local function setup_zlib_system()
    return false
end

local function setup_zlib_prebuilt()
    return false
end

local function setup_zlib_source()
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
        BoltPkgConfig.pkg_config('minizip', 'minizip')
    end)
end

local function setup_minizip_system()
    return false
end

local function setup_minizip_prebuilt()
    return false
end

local function setup_minizip_source()
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