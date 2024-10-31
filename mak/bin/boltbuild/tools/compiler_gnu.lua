---@type Context
local context = ...

GnuCompiler = {}

---Retrieves some GCC specifications and store them in the current context environment
---@param command (string|Node)[]) The command to execute for the compiler.
---@param language string The name of the language (uppercase, C or CXX).
function GnuCompiler.get_specs(command, language)
    local env = context.env
    for _, arg in ipairs(env[language..'FLAGS']) do
        command[1 + #command] = arg
    end
    command[1 + #command] = '-v'
    command[1 + #command] = '-dM'
    command[1 + #command] = '-E'
    command[1 + #command] = '-'

    local handle = context:popen(command)
    local success, out, err = handle:communicate()
    if not success then
        error(err)
    end

    env.TARGET = target

    ---@type table<string, string>
    local defines = {}
    ---@type Node[]
    local includes = {}
    local search_paths = false
    local arch = nil
    local endianness = nil
    local sizeof_pointer = nil

    for line in (err + out):lines() do
        if string.starts_with(line, "#include <...>") then
            search_paths = true
        elseif search_paths then
            if string.starts_with(line, "End of search list") then
                search_paths = false
            else
                local path = context.path:make_node(string.trim(line))
                includes[#includes + 1] = path
            end
        else
            local s, _, name, value = line:find('%s*#%s*define%s+([%w_]+)%s*(.*)')
            if s then
                defines[name] = value
                env:append(language.."_COMPILER_SYSTEM_DEFINES", tostring(name)..'='..tostring(value))
                if name == '__MACH__' then
                    env.BINARY_FORMAT = 'mach'
                elseif name == '__ELF__' then
                    env.BINARY_FORMAT = 'elf'
                elseif name == '_WIN32' then
                    env.BINARY_FORMAT = 'pe'
                    env.TARGET_OS = 'windows'
                elseif name == '__ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__' then
                    env.TARGET_OS = 'macos'
                elseif name == '__ENVIRONMENT_IPHONE_OS_VERSION_MIN_REQUIRED__' then
                    env.TARGET_OS = 'ios'
                elseif name == '__ENVIRONMENT_WATCH_OS_VERSION_MIN_REQUIRED__' then
                    env.TARGET_OS = 'watchos'
                elseif name == '__ENVIRONMENT_TV_OS_VERSION_MIN_REQUIRED__' then
                    env.TARGET_OS = 'tvos'
                elseif name == '__linux__' then
                    if env.TARGET_OS == nil then
                        env.TARGET_OS = 'linux'
                    end
                elseif name == '__FreeBSD__' then
                    env.TARGET_OS = 'freebsd'
                elseif name == '__sun__' then
                    env.TARGET_OS = 'solaris'
                elseif name == '__ANDROID__' then
                    env.TARGET_OS = 'android'
                elseif name == '__LITTLE_ENDIAN__' then
                    endianness = 'little'
                elseif name == '__BIG_ENDIAN__' then
                    endianness = 'big'
                elseif name == '__SIZEOF_POINTER__' then
                    sizeof_pointer = tonumber(value) * 8
                elseif name == '__x86_64__' then
                    arch = 'amd64'
                elseif name == '__i386__' then
                    arch = 'x86'
                elseif name == '__powerpc64__' then
                    arch = 'ppc64'
                elseif name == '__powerpc__' then
                    if arch == nil then
                        arch = 'ppc'
                    end
                elseif name == '__arm__' then
                    if arch == nil then
                        arch = 'arm'
                    end
                elseif name == '__aarch64__' then
                    arch = 'arm64'
                end
            end
        end
    end

    env[language.."_COMPILER_SYSTEM_INCLUDES"] = includes
    if env.BINARY_FORMAT == 'mach' then
        env.PROGRAM_PATTERN = '%s'
        env.SHLIB_PATTERN = '%s.dylib'
        env.STLIB_PATTERN = '%s.a'
    elseif env.BINARY_FORMAT == 'elf' then
        env.PROGRAM_PATTERN = '%s'
        env.SHLIB_PATTERN = '%s.so'
        env.STLIB_PATTERN = '%s.a'
    elseif env.BINARY_FORMAT == 'pe' then
        env.PROGRAM_PATTERN = '%s.exe'
        env.SHLIB_PATTERN = '%s.dylib'
        env.STLIB_PATTERN = '%s.a'
    else
        context:warn('unable to determine binary format')
        env.PROGRAM_PATTERN = '%s'
        env.SHLIB_PATTERN = '%s.so'
        env.STLIB_PATTERN = '%s.a'
    end

    if arch == nil then
        context:warn('unable to determine target architecture')
        arch = 'unknown'
    else
        if arch == 'arm64' and sizeof_pointer == 32 then
            arch = 'arm64_32'
        end
        if arch == 'amd64' and sizeof_pointer == 32 then
            arch = 'x32'
        end

        if (arch == 'arm' or arch == 'arm64') and endianness == 'big' then
            arch = arch + 'eb'
        end
        if (arch == 'ppc' or arch == 'ppc64') and endianness == 'little' then
            arch = arch + 'le'
        end
    end
    env.ARCHITECTURE = arch
    return defines
end
