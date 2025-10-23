---@type Context
local context = ...

context:load_tool('utils/string_ext')
context:load_tool('internal/binfmt')

--- Explore a directory looking for additional systems for macOS, Linux, Windows, freeBSD, etc
--- @param path string The root directory to explore
--- @return Environment[] #A table of discovered sysroot systems.
function find_sysroot_systems(path)
    local sysroot_node = context.path:make_node(path)
    local result = {}
    if not sysroot_node:is_dir() then
        return result
    end

    local cl_paths = context:search(sysroot_node,
        'program files*/microsoft visual studio/*/*/vc/tools/msvc/*/lib/*/libcmt.lib')
    local sdk_paths = context:search(sysroot_node,
        'program files*/windows kits/10/lib/*/ucrt/*/libucrt.lib')

    if #cl_paths > 0 and #sdk_paths > 0 then
        -- only use the highest windows SDK installed
        local sdk_path = sdk_paths[#sdk_paths].parent.parent.parent
        local sdk_version = sdk_path:name()
        sdk_path = sdk_path.parent.parent
        local seen = {}
        for _, cl_path in ipairs(cl_paths) do
            local msvc_path = cl_path.parent
            local arch = msvc_path:name()
            msvc_path = msvc_path.parent.parent
            local version = msvc_path:name()
            local key = arch .. '-' .. version

            if not seen[key] then
                local env = context:new_env()
                env.SYSROOT = msvc_path
                local include = sdk_path:make_node('include'):make_node(sdk_version)
                env.TARGET = 'windows-msvc'
                env.ARCH = arch
                env.VERSION = version
                env.INCLUDES = {
                    msvc_path:make_node('include'),
                    include:make_node('ucrt'),
                    include:make_node('shared'),
                    include:make_node('um'),
                    include:make_node('winrt'),
                }
                env.LIBPATHS = {
                    msvc_path:make_node('lib'):make_node(arch),
                    sdk_path:make_node('lib'):make_node(sdk_version):make_node('ucrt'):make_node(arch),
                    sdk_path:make_node('lib'):make_node(sdk_version):make_node('um'):make_node(arch),
                }
                result[#result + 1] = env
                seen[key] = true
            end
        end
    end

    return result
end

if context.name == 'init' then
    local mounts = context.path:make_node('/proc/mounts'):read():split('\n')
    for _, line in ipairs(mounts) do
        local parts = line:split(' ')
        local mount_point = parts[2]
        if mount_point ~= '/' then
            context.env:append('SYSROOTS_INIT', find_sysroot_systems(mount_point))
        end
    end

    context.settings:add_list('sysroots', 'List of paths to use when searching for compilers and tools.', {})
        :set_long('sysroots')
        :set_category('Options controlling the configuration')
else
    if not context.env.SYSROOTS_DONE then
        for _, sysroot in ipairs(context.env.SYSROOTS_INIT or {}) do
            context.env:append('SYSROOTS', sysroot)
        end
        for _, sysroot in ipairs(context.settings.sysroots or {}) do
            context.env:append('SYSROOTS', find_sysroot_systems(sysroot))
        end
        context.env.SYSROOTS_DONE = true
    end
end
