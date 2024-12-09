---@type Context
local context = ...

context:load_tool('internal/compiler_gnu')
context:load_tool('utils/string_ext')

Bolt.Clang = {}

local function vswhere_clang()
    local compilers = {}
    context:try('Running vswhere', function()
        local p = context:popen({
            'C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\vswhere.exe',
            '-all',
            '-products',
            '*',
            '-find',
            'VC\\Tools\\Llvm\\bin',
        })
        local result, out, err = p:communicate('')
        if result then
            for path in out:lines() do
                path = context.path:make_node(path)
                clang = context:find_program('clang', { path })
                if clang then
                    table.insert(compilers, clang)
                end
            end
        end
    end)
    return compilers
end

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

local function load_clang(env, compiler, flags, lang, var)
    env[var .. 'FLAGS'] = { '-x', lang, '-c', '-fPIC' }
    env:append(var .. 'FLAGS', flags)
    env[var .. '_COMPILER_NAME'] = 'clang'
    env[var .. '_TGT_F'] = '-o'
    env[var .. '_DEFINE_ST'] = '-D'
    env[var .. '_INCLUDE_ST'] = '-I'
    env[var .. '_SYSTEM_INCLUDE_ST'] = '-isystem%s'
    env[var .. '_IDIRAFTER'] = '-idirafter'
    env[var .. 'FLAGS.warn.none'] = { '-w'}
    env[var .. 'FLAGS.warn.all'] = { '-Wall', '-Wextra', '-Wpedantic' }
    env.LINK = env.CLANG
    env.LINKFLAGS = {}
    env.LINK_TGT_F = '-o'
    env.LINK_LIB_F = '-l'
    env.LINK_LIBPATH_F = '-L'
    env.LINKFLAGS_shlib = { '-shared' }
    env['CLANG_' .. var .. '_VERSION'] = get_clang_version(Bolt.GnuCompiler.get_specs(compiler, var))
    if env.BINARY_FORMAT == 'elf' then
        env:append('LINKFLAGS_shlib', '-Wl,-z,defs')
    end

    context:load_tool('internal/' .. lang)
    context:load_tool('internal/link')
    env.LIB = context:find_program(env.TARGET..'-ar')
    if not env.LIB then
        env.LIB = context:find_program('ar')
    end
    env.LIBFLAGS = { 'rcs' }
end

--- Loads the C compiler settings into the environment.
--- This function configures the environment to use the Clang compiler for C.
--- It sets the necessary flags and libraries required for C compilation.
--- The function uses `context.env.CLANG` as the base clang command.
---
--- The function raises an error if the compiler command returns an error code.
---
--- @param c_flags string[] A table containing extra flags that the C compiler should support.
function Bolt.Clang.load_c(c_flags)
    local env = context.env
    env.CC = env.CLANG
    load_clang(env, env.CC, c_flags, 'c', 'C')
end

--- Loads the C++ compiler settings into the environment.
--- This function configures the environment to use the Clang compiler for C++.
--- It sets the necessary flags and libraries required for C++ compilation.
--- The function uses `context.env.CLANG` as the base clang command.
---
--- An error is raised if the compiler command returns an error code.
---
--- @param cxx_flags string[] A table containing extra flags that the C++ compiler should support.
function Bolt.Clang.load_cxx(cxx_flags)
    local env = context.env
    env.CXX = env.CLANG
    env.LIBS = { 'stdc++' }
    load_clang(env, env.CXX, cxx_flags, 'c++', 'CXX')
end

--- Loads the Objective-C compiler settings into the environment.
--- This function configures the environment to use the Clang compiler for Objective-C.
--- It sets the necessary flags and libraries required for Objective-C compilation.
--- The function uses `context.env.CLANG` as the base clang command.
---
--- An error is raised if the compiler command returns an error code.
---
--- @param objc_flags string[] A table containing extra flags that the Objective-C compiler should support.
function Bolt.Clang.load_objc(objc_flags)
    local env = context.env
    env.OBJC = env.CLANG
    env.LIBS = { 'objc' }
    load_clang(env, env.OBJC, objc_flags, 'objc', 'OBJC')
end

--- Loads the Objective-C++ compiler settings into the environment.
--- This function configures the environment to use the Clang compiler for Objective-C++.
--- It sets the necessary flags and libraries required for Objective-C++ compilation.
--- The function uses `context.env.CLANG` as the base clang command.
---
--- An error is raised if the compiler command returns an error code.
---
--- @param objcxx_flags string[] A table containing extra flags that the Objective-C++ compiler should support.
function Bolt.Clang.load_objcxx(objcxx_flags)
    local env = context.env
    env.OBJCXX = env.CLANG
    env.LIBS = { 'objc' }
    load_clang(env, env.OBJCXX, objcxx_flags, 'objc++', 'OBJCXX')
end

local languages = {
    ['c'] = Bolt.Clang.load_c,
    ['c++'] = Bolt.Clang.load_cxx,
    ['objc'] = Bolt.Clang.load_objc,
    ['objc++'] = Bolt.Clang.load_objcxx,
}

local function detect_clang_targets(clang, callback, language_flags, global_flags)
    local command
    if #global_flags == 0 then
        command = { clang, '-v', '-E', '-' }
    else
        command = { clang, #global_flags, '-v', '-E', '-' }
    end
    local _, out, err = context:popen(command):communicate()
    local search_paths, paths, seen = false, {}, {}

    for line in (err + out):lines() do
        line = string.trim(line)
        if line:find("#include <...>") then
            search_paths = true
        elseif line:find("ignoring nonexistent directory") then
            table.insert(paths, context.path:make_node(line:sub(33, -2)))
        elseif search_paths and line:find("End of search list") then
            break
        elseif search_paths then
            table.insert(paths, context.path:make_node(line))
        end
    end

    local default_triple
    local triples = { }
    for _, path in ipairs(paths) do
        local component, relpath, component_count = path:name(), '', 1
        while component do
            path = path.parent
            local component_list = string.split(component, '-')
            if #component_list >= 2 then
                for _, triple in ipairs(context:search(path, '*-*/' .. relpath .. '/sys', true)) do
                    default_triple = component
                    for _ = 1, component_count do
                        triple = triple.parent
                    end
                    triple = triple:name()
                    if not seen[triple] then
                        seen[triple] = true
                        table.insert(triples, triple)
                    end
                end
            end
            relpath = component .. '/' .. relpath
            component_count = component_count + 1
            component = path:name()
        end
    end
    -- sort by triple, keeping the default triple at the top of the list
    table.sort(triples, function(a, b)
        if a == default_triple then
            return true
        end
        if b == default_triple then
            return false
        end
        return a < b
    end)
    for _, triple in ipairs(triples) do
        context:try('running clang ' .. clang:abs_path() .. ' for target ' .. triple, function()
            local env = context:derive()
            context:with(env, function()
                context.env.TRIPLE = triple
                context.env.CLANG = { clang, '-target', triple, table.unpack(global_flags) }
                for lang, flags in pairs(language_flags) do
                    languages[lang](flags)
                end
            end)
            if callback(env) ~= true then
                return false
            end
        end)
    end
    return true
end

--- Discovers available Clang compilers and their targets.
--- This function searches for Clang compilers in the environment paths and optionally detects the available targets.
--- It then loads the compiler in a new environment and calls the specified callback. The callback can end the search by
--- returning `nil` or `false`; otherwise, the discovery resumes.
---
--- @param callback fun(env:Environment):(boolean|nil) A callback function to be executed for each discovered compiler. The function should return `true` to continue the discovery, or `nil`/`false` to stop.
--- @param language_flags table<string, string[]> A table where keys are language names (e.g., 'c', 'c++') and values are arrays of extra flags that the compiler should support for each language.
--- @param global_flags string[]|nil An optional array of additional language-independent flags to be passed to the compiler.
--- @param detect_cross_targets boolean|nil An optional boolean value indicating whether to detect cross-compilation targets. If `true`, the function will attempt to detect and include cross-compilation targets.
function Bolt.Clang.discover(callback, language_flags, global_flags, detect_cross_targets)
    local seen = {}
    local compilers = {}
    global_flags = global_flags or {}
    context:try('Looking for Clang compilers', function()
        for _, path in ipairs(context.settings.path) do
            for _, node in ipairs(context:search(path, 'clang*' .. context.settings.exe_suffix)) do
                local version = node:name():match("^clang%-?(%d*)" .. context.settings.exe_suffix .. "$")
                if version ~= nil and node:is_file() then
                    node = node:read_link()
                    local absolute_path = node:abs_path()
                    if not seen[absolute_path] then
                        seen[absolute_path] = true
                        table.insert(compilers, { version, node })
                    end
                end
            end
        end
        for _, clang in ipairs(vswhere_clang()) do
            table.insert(compilers, { '', clang })
        end
        -- sort by decreasing version. Highest priority is the default compiler (the one with no version number)
        table.sort(compilers, function(a, b)
            if a[1] == "" then
                return true
            end
            if b[1] == "" then
                return false
            end
            return tonumber(a[1]) > tonumber(b[1])
        end)
        for _, compiler in ipairs(compilers) do
            if detect_cross_targets then
                if detect_clang_targets(compiler[2], callback, language_flags, global_flags) ~= true then
                    return tostring(compiler[2])
                end
            else
                context:try('running clang ' .. compiler[2]:abs_path(), function()
                    local env = context:derive()
                    context:with(env, function()
                        context.env.CLANG = { compiler[2] }
                        context.env:append('CLANG', global_flags)
                        for lang, flags in pairs(language_flags) do
                            languages[lang](flags)
                        end
                        context.env.TRIPLE = context.env.TARGET
                    end)
                    if callback(env) ~= true then
                        return 'done'
                    end
                end)
            end
        end
        return 'done'
    end)
end
