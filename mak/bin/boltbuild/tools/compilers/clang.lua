---@type Context
local context = ...

context:load_tool('bolt')
context:load_tool('internal/compiler_gnu')
context:load_tool('utils/string_ext')

Bolt.Clang = {}

local function get_clang_version(defines)
    local version = { 0, 0, 0 }
    for name, value in pairs(defines) do
        if name == '__clang_major__' then
            version[1] = tonumber(value)
        elseif name == '__clang_minor__' then
            version[2] = tonumber(value)
        elseif name == '__clang_patchlevel__' then
            version[3] = tonumber(value)
        end
    end
    return table.concat(version, '.')
end

local function load_clang(env, compiler, flags, link_flags, lang, var)
    env[var .. 'FLAGS'] = { '-x', lang, '-c', '-fPIC' }
    env:append(var .. 'FLAGS', flags)
    env[var .. '_COMPILER_NAME'] = 'clang'
    env[var .. '_TGT_F'] = '-o'
    env[var .. '_DEFINE_ST'] = '-D'
    env[var .. '_INCLUDE_ST'] = '-I'
    env[var .. '_SYSTEM_INCLUDE_ST'] = '-isystem%s'
    env.LINKFLAGS = link_flags
    env.LINK_TGT_F = '-o'
    env.LINK_LIB_F = '-l'
    env.LINK_LIBPATH_F = '-L'
    env.LINKFLAGS_shlib = '-shared'
    env['CLANG_' .. var .. '_VERSION'] = get_clang_version(GnuCompiler.get_specs(compiler, var))
    context:load_tool('internal/' .. lang)
    context:load_tool('internal/link')
end

function Bolt.Clang.load_clang_c(c_flags, link_flags)
    local env = context.env
    env.CC = env.CC or { 'clang' }
    env.LINK = env.CC
    load_clang(env, env.CC, c_flags, link_flags, 'c', 'C')
end

function Bolt.Clang.load_clang_cxx(cxx_flags, link_flags)
    local env = context.env
    env.CXX = env.CC or { 'clang++' }
    env.LINK = env.CXX
    load_clang(env, env.CXX, cxx_flags, link_flags, 'c++', 'CXX')
end

function Bolt.Clang.detect_clang_targets(clang, c_flags, cxx_flags)
    local c_command
    c_flags = c_flags or {}
    cxx_flags = cxx_flags or {}
    if #c_flags == 0 then
        c_command = { clang, '-x', 'c', '-v', '-E', '-' }
    else
        c_command = { clang, table.unpack(c_flags), '-x', 'c', '-v', '-E', '-' }
    end
    local result, seen = {}, {}
    local _, out, err = context:popen(c_command):communicate()
    local search_paths, paths = false, {}

    for line in (err + out):lines() do
        line = string.trim(line)
        if line:find("#include <...>") then
            search_paths = true
        elseif line:find("ignoring nonexistent directory") then
            paths[#paths + 1] = context.path:make_node(line:sub(33, -2))
        elseif search_paths and line:find("End of search list") then
            break
        elseif search_paths then
            paths[#paths + 1] = context.path:make_node(line)
        end
    end

    for _, path in ipairs(paths) do
        local component, relpath, component_count = path:name(), '', 1
        while component do
            path = path.parent
            local component_list = string.split(component, '-')
            if #component_list >= 2 then
                for _, triple in ipairs(context:search(path, '*-*/' .. relpath .. '/sys', true)) do
                    for i = 1, component_count do
                        triple = triple.parent
                    end
                    triple = triple:name()
                    if not seen[triple] then
                        seen[triple] = true
                        if context:try('running clang ' .. clang:abs_path() .. ' for target ' .. triple, function()
                            context:with(context:derive(), function()
                                local c_target_flags, cxx_target_flags
                                if #c_flags ~= 0 then
                                    c_target_flags = { '-target', triple, table.unpack(c_flags) }
                                else
                                    c_target_flags = { '-target', triple }
                                end
                                if #cxx_flags ~= 0 then
                                    cxx_target_flags = { '-target', triple, table.unpack(cxx_flags) }
                                else
                                    cxx_target_flags = { '-target', triple }
                                end
                                context.env.CC = { clang }
                                Bolt.Clang.load_clang_c(c_target_flags, { '-target', triple })
                                Bolt.Clang.load_clang_cxx(cxx_target_flags, { '-target', triple })
                                result[#result + 1] = context.env
                            end)
                        end) then
                            break
                        end
                    end
                end
            end
            relpath = component .. '/' .. relpath
            component_count = component_count + 1
            component = path:name()
        end
    end
    return result
end

function Bolt.Clang.discover(c_flags, cxx_flags)
    local result, seen = {}, {}
    context:try('Looking for Clang compilers', function()
        for _, path in ipairs(context.settings.path) do
            for _, node in ipairs(context:search(path, 'clang*' .. context.settings.exe_suffix)) do
                local version = node:name():match("^clang%-?(%d*)" .. context.settings.exe_suffix .. "$")
                if version and node:is_file() then
                    node = node:read_link()
                    local absolute_path = node:abs_path()
                    if not seen[absolute_path] then
                        seen[absolute_path] = true
                        for _, env in ipairs(Bolt.Clang.detect_clang_targets(node, c_flags, cxx_flags)) do
                            env.CLANG_VERSION = version
                            result[#result + 1] = env
                        end
                    end
                end
            end
        end
        return 'done'
    end)
    return result
end