---@type Context
local context = ...

context:load_tool('bolt')
context:load_tool('internal/compiler_gnu')

Bolt.Gcc = {}

---@param c_flags (string|Node)[]) The flags to pass to the compiler.
function Bolt.Gcc.load_gcc_c(c_flags)
    local env = context.env

    env.CFLAGS = {'-x', 'c', '-c', '-fPIC'}
    env:append('CFLAGS', c_flags)
    env.C_COMPILER_NAME = 'gcc'
    env.C_TGT_F = '-o'
    env.C_DEFINE_ST = '-D'
    env.C_INCLUDE_ST = '-I'
    env.C_SYSTEM_INCLUDE_ST = '-isystem%s'
    env.C_IDIRAFTER = '-isystem'
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

    env.GCC_C_VERSION = table.concat(version, '.')

    context:load_tool('internal/c')
    context:load_tool('internal/link')
end

---@param cxx_flags (string|Node)[]) The flags to pass to the compiler.
function Bolt.Gcc.load_gcc_cxx(cxx_flags)
    local env = context.env
    if env.CC and env.C_COMPILER_NAME == 'gcc' then
        env.CXX = env.CC
    else
        context:error('Could not find a valid GCC c++ compiler')
    end

    env.CXXFLAGS = {'-x', 'c++', '-c', '-fPIC'}
    env:append('CXXFLAGS', cxx_flags)
    env.CXX_COMPILER_NAME = 'gcc'
    env.CXX_TGT_F = '-o'
    env.CXX_DEFINE_ST = '-D'
    env.CXX_INCLUDE_ST = '-I'
    env.CXX_SYSTEM_INCLUDE_ST = '-isystem%s'
    env.CXX_IDIRAFTER = '-isystem'
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
    env.GCC_CXX_VERSION = table.concat(version, '.')

    context:load_tool('internal/c++')
    context:load_tool('internal/link')
end

---@param c_flags (string|Node)[]|nil Extra flags that the C compiler should support.
---@param cxx_flags (string|Node)[]|nil Extra flags that the C++ compiler should support.
---@return Environment[] A list of environments where a Clang compiler has been loaded.
function Bolt.Gcc.discover(c_flags, cxx_flags)
    c_flags = c_flags or {}
    cxx_flags = cxx_flags or {}
    local result = {}
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
                            context:with(context:derive(), function()
                                context.env.CC = { gcc }
                                context.env.GCC_VERSION = version
                                Bolt.Gcc.load_gcc_c(c_flags)
                                Bolt.Gcc.load_gcc_cxx(cxx_flags)
                                result[#result + 1] = context.env
                            end)
                        end) then
                            for _, multilib in ipairs(context:search(crtbegin.parent, '*/crtbegin.o')) do

                                local multilib_c_flags, multilib_cxx_flags
                                if #c_flags ~= 0 then
                                    multilib_c_flags = { table.unpack(c_flags), '-m' .. multilib.parent:name() }
                                else
                                    multilib_c_flags = { '-m' .. multilib.parent:name() }
                                end
                                if #cxx_flags ~= 0 then
                                    multilib_cxx_flags = { table.unpack(cxx_flags), '-m' .. multilib.parent:name() }
                                else
                                    multilib_cxx_flags = { '-m' .. multilib.parent:name() }
                                end
                                pcall(function()
                                    context:with(context:derive(), function()
                                        context.env.CC = { gcc }
                                        context.env.GCC_VERSION = version
                                        Bolt.Gcc.load_gcc_c(multilib_c_flags)
                                        Bolt.Gcc.load_gcc_cxx(multilib_cxx_flags)
                                        result[#result + 1] = context.env
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