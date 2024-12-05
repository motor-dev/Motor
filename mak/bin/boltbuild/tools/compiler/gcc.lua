---@type Context
local context = ...

context:load_tool('internal/compiler_gnu')

Bolt.GCC = {}

local function load_gcc_compiler(env, compiler, flags, language, var_name)
    env[var_name .. 'FLAGS'] = { '-x', language, '-c', '-fPIC' }
    env:append(var_name .. 'FLAGS', flags)
    env[var_name .. '_COMPILER_NAME'] = 'gcc'
    env[var_name .. '_TGT_F'] = '-o'
    env[var_name .. '_DEFINE_ST'] = '-D'
    env[var_name .. '_INCLUDE_ST'] = '-I'
    env[var_name .. '_SYSTEM_INCLUDE_ST'] = '-isystem%s'
    env[var_name .. '_IDIRAFTER'] = '-isystem'
    env.LINK = env.GCC
    env.LINKFLAGS = {}
    env.LINK_TGT_F = '-o'
    env.LINK_LIB_F = '-l'
    env.LINK_LIBPATH_F = '-L'
    env.LINKFLAGS_shlib = { '-shared' }

    local defines = Bolt.GnuCompiler.get_specs(compiler, var_name)
    local version = { 0, 0, 0 }

    for name, value in pairs(defines) do
        if name == '__GNUC__' then
            version[1] = tonumber(value)
        elseif name == '__GNUC_MINOR__' then
            version[2] = tonumber(value)
        elseif name == '__GNUC_PATCHLEVEL__' then
            version[3] = tonumber(value)
        end
    end

    env['GCC_' .. var_name .. '_VERSION'] = table.concat(version, '.')

    if env.BINARY_FORMAT == 'elf' then
        env:append('LINKFLAGS_shlib', '-Wl,-z,defs')
    end

    context:load_tool('internal/' .. language)
    context:load_tool('internal/link')
end

--- Loads the C compiler settings into the environment.
--- This function configures the environment to use the Gcc compiler for C.
--- It sets the necessary flags and libraries required for C compilation.
--- The function uses `context.env.GCC` as the base compiler command.
---
--- An error is raised if the compiler command returns an error code.
---
--- @param c_flags string[] A table containing extra flags that the C compiler should support.
function Bolt.GCC.load_c(c_flags)
    local env = context.env
    env.CC = env.GCC
    load_gcc_compiler(env, env.CC, c_flags, 'c', 'C')
end

--- Loads the C++ compiler settings into the environment.
--- This function configures the environment to use the Gcc compiler for C++.
--- It sets the necessary flags and libraries required for C++ compilation.
--- The function uses `context.env.GCC` as the base compiler command.
---
--- An error is raised if the compiler command returns an error code.
---
--- @param cxx_flags string[] A table containing extra flags that the C++ compiler should support.
function Bolt.GCC.load_cxx(cxx_flags)
    local env = context.env
    env.CXX = env.GCC
    env.LIBS = { 'stdc++' }
    load_gcc_compiler(env, env.CXX, cxx_flags, 'c++', 'CXX')
end

--- Loads the Objective-C compiler settings into the environment.
--- This function configures the environment to use the Gcc compiler for Objective-C.
--- It sets the necessary flags and libraries required for Objective-C compilation.
--- The function uses `context.env.GCC` as the base compiler command.
---
--- An error is raised if the compiler command returns an error code.
---
--- @param objc_flags string[] A table containing extra flags that the Objective-C compiler should support.
function Bolt.GCC.load_objc(objc_flags)
    local env = context.env
    env.OBJC = env.GCC
    env.LIBS = { 'objc' }
    load_gcc_compiler(env, env.OBJC, objc_flags, 'objc', 'OBJC')
end

--- Loads the Objective-C++ compiler settings into the environment.
--- This function configures the environment to use the Gcc compiler for Objective-C++.
--- It sets the necessary flags and libraries required for Objective-C++ compilation.
--- The function uses `context.env.GCC` as the base compiler command.
---
--- An error is raised if the compiler command returns an error code.
---
--- @param objcxx_flags string[] A table containing extra flags that the Objective-C++ compiler should support.
function Bolt.GCC.load_objcxx(objcxx_flags)
    local env = context.env
    env.OBJCXX = env.GCC
    env.LIBS = { 'stdc++', 'objc' }
    load_gcc_compiler(env, env.OBJCXX, objcxx_flags, 'objc++', 'OBJCXX')
end

local languages = {
    ['c'] = Bolt.GCC.load_c,
    ['c++'] = Bolt.GCC.load_cxx,
    ['objc'] = Bolt.GCC.load_objc,
    ['objc++'] = Bolt.GCC.load_objcxx,
}

--- Discovers available GCC compilers and configures the environment for each found compiler.
--- This function searches for GCC compilers in the specified paths, configures the environment
--- for each found compiler, and invokes the callback function with the configured environment.
--- It also supports detecting multilib configurations.
---
--- @param callback fun(env:Environment):(boolean|nil) The function to call with the configured environment.
--- @param language_flags table A table containing flags for each language to pass to the compiler.
--- @param global_flags table A table containing global flags to pass to the compiler.
--- @param detect_multilib boolean Whether to detect and configure multilib environments.
function Bolt.GCC.discover(callback, language_flags, global_flags, detect_multilib)
    context:try('Looking for Gcc compilers', function()
        local seen = {}
        local paths = context.settings.path

        for _, path in ipairs(paths) do
            for _, crtbegin in ipairs(context:search(path.parent, 'lib/gcc*/*/*/crtbegin.o')) do
                crtbegin = crtbegin:canonicalize()
                if not seen[crtbegin:abs_path()] then
                    local node = crtbegin.parent
                    local version = node:name()
                    node = node.parent
                    local target = node:name()
                    for _, gcc in ipairs(context:search(path, target .. '-gcc-' .. version .. context.settings.exe_suffix)) do
                        seen[crtbegin:abs_path()] = crtbegin
                        if pcall(function()
                            local env = context:derive()
                            context:with(env, function()
                                context.env.TRIPLE = target
                                context.env.GCC = { gcc }
                                context.env:append('GCC', global_flags)
                                context.env.GCC_VERSION = version
                                for lang, flags in pairs(language_flags) do
                                    languages[lang](flags)
                                end
                            end)
                            if callback(env) ~= true then
                                return tostring(gcc)
                            end
                        end) and detect_multilib then
                            for _, multilib in ipairs(context:search(crtbegin.parent, '*/crtbegin.o')) do
                                pcall(function()
                                    local env = context:derive()
                                    context:with(env, function()
                                        context.env.TRIPLE = target
                                        context.env.CC = { gcc }
                                        context.env:append('GCC', global_flags)
                                        context.env:append('GCC', '-m' .. multilib.parent:name())
                                        context.env.GCC_VERSION = version
                                        for lang, flags in pairs(language_flags) do
                                            languages[lang](flags)
                                        end
                                    end)
                                    if callback(env) ~= true then
                                        return tostring(gcc)
                                    end
                                end)
                            end
                            break
                        end
                    end
                end
            end
        end
        return 'done'
    end)
end