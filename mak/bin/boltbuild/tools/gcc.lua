---@type Context
local context = ...

context:load_tool('compiler_gnu')

Gcc = {}

---@param c_flags (string|Node)[]) The flags to pass to the compiler.
function Gcc.load_gcc_c(c_flags)
    local env = context.env

    env.CFLAGS = {'-x', 'c', '-c', '-fPIC'}
    env:append('CFLAGS', c_flags)
    env.C_COMPILER_NAME = 'gcc'
    env.CC_TGT_F = '-o'
    env.CC_DEFINE_ST = '-D'
    env.CC_INCLUDE_ST = '-I'
    env.CC_SYSTEM_INCLUDE_ST = '-isystem%s'
    env.LINK = env.CC
    env.LINKFLAGS = {}
    env.LINK_TGT_F = '-o'
    env.LINK_LIB_F = '-l'
    env.LINK_LIBPATH_F = '-L'
    env.LINKFLAGS_shlib = '-shared'

    local defines = GnuCompiler.get_specs(env.CC, "C")
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

    env.GCC_C_VERSION = version[1] .. '.' .. version[2] .. '.' .. version[3]
end

---@param cxx_flags (string|Node)[]) The flags to pass to the compiler.
function Gcc.load_gcc_cxx(cxx_flags)
    local env = context.env
    -- if a  GCC C compiler is loaded, use that
    if env.CC and env.C_COMPILER_NAME == 'gcc' then
        env.CXX = env.CC
    else
        -- todo
        context:error('Could not find a valid GCC c++ compiler')
    end

    env.CXXFLAGS = {'-x', 'c++', '-c', '-fPIC'}
    env:append('CXXFLAGS', cxx_flags)
    env.CXX_COMPILER_NAME = 'gcc'
    env.CXX_TGT_F = '-o'
    env.CXX_DEFINE_ST = '-D'
    env.CXX_INCLUDE_ST = '-I'
    env.CXX_SYSTEM_INCLUDE_ST = '-isystem%s'
    env.LINK = env.CXX
    env.LINKFLAGS = {}
    env.LINK_TGT_F = '-o'
    env.LINK_LIB_F = '-l'
    env.LINK_LIBPATH_F = '-L'
    env.LINKFLAGS_shlib = '-shared'

    local defines = GnuCompiler.get_specs(env.CXX, "CXX")
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
    env.GCC_CXX_VERSION = version[1] .. '.' .. version[2] .. '.' .. version[3]
end

---Discover as many Gcc compilers as possible, including extra triples where applicable. When gcc compilers are found,
---load the compiler in a new environment derived from the current environment.
---@param c_flags (string|Node)[]? Extra flags that the C compiler should support.
---@param cxx_flags (string|Node)[]? Extra flags that the C++ compiler should support.
---@return Environment[] A list of environments where a Clang compiler has been loaded.
function Gcc.discover(c_flags, cxx_flags)
    if c_flags == nil then
        c_flags = {}
    end
    if cxx_flags == nil then
        cxx_flags = {}
    end
    local result = {}
    context:try('Looking for Gcc compilers', function()
        ---@type table<string, Node>
        local seen = {}
        local paths = context.settings.path

        for _, path in ipairs(--[[---@type Node[] ]] paths) do
            for _, crtbegin in ipairs(context:search(path.parent, 'lib/gcc*/*/*/crtbegin.o')) do
                crtbegin = crtbegin:canonicalize()
                if seen[crtbegin:abs_path()] == nil then
                    local node = crtbegin.parent
                    local version = node:name()
                    node = node.parent
                    local target = node:name()
                    for _, gcc in ipairs(context:search(path, target .. '-gcc-' .. version .. context.settings.exe_suffix)) do
                        seen[crtbegin:abs_path()] = crtbegin
                        if pcall(function()
                            context:with(context:derive(), function()
                                context.env.CC = { gcc }
                                context.env.GCC_VERSION = version
                                Gcc.load_gcc_c(c_flags)
                                Gcc.load_gcc_cxx(cxx_flags)
                                result[1 + #result] = context.env
                            end)
                        end) then
                            for _, multilib in ipairs(context:search(crtbegin.parent, '*/crtbegin.o')) do
                                multilib = multilib.parent:name()
                                local multilib_c_flags = {}
                                local multilib_cxx_flags = {}
                                for _, flag in ipairs(c_flags) do
                                    multilib_c_flags[1 + #multilib_c_flags] = flag
                                end
                                for _, flag in ipairs(cxx_flags) do
                                    multilib_cxx_flags[1 + #multilib_cxx_flags] = flag
                                end
                                multilib_c_flags[1 + #multilib_c_flags] = '-m' .. multilib
                                multilib_cxx_flags[1 + #multilib_cxx_flags] = '-m' .. multilib
                                pcall(function()
                                    context:with(context:derive(), function()
                                        context.env.CC = { gcc }
                                        context.env.GCC_VERSION = version
                                        Gcc.load_gcc_c(multilib_c_flags)
                                        Gcc.load_gcc_cxx(multilib_cxx_flags)
                                        result[1 + #result] = context.env
                                    end)
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
    return result
end

-- load build rules for C and C++
context:load_tool('c')
context:load_tool('cxx')
