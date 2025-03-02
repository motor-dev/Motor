---@type Context
local context = ...
context:load_tool('internal/bolt')

Bolt.MSVC = {}

local MSVC_PREDEFINED_MACROS = {
    '__cplusplus',
    '__STDC__',
    '__STDC_HOSTED__',
    '__STDC_NO_ATOMICS__',
    '__STDC_NO_COMPLEX__',
    '__STDC_NO_THREADS__',
    '__STDC_NO_VLA__',
    '__STDC_VERSION__',
    '__STDCPP_DEFAULT_NEW_ALIGNMENT__',
    '__STDCPP_THREADS__',
    '__ATOM__',
    '__AVX__',
    '__AVX2__',
    '__AVX512BW__',
    '__AVX512CD__',
    '__AVX512DQ__',
    '__AVX512F__',
    '__AVX512VL__',
    '_CHAR_UNSIGNED',
    '__CLR_VER',
    '_CONTROL_FLOW_GUARD',
    '__cplusplus_cli',
    '__cplusplus_winrt',
    '_CPPRTTI',
    '_CPPUNWIND',
    '_DEBUG',
    '_DLL',
    '_INTEGRAL_MAX_BITS',
    '_ISO_VOLATILE',
    '_M_AMD64',
    '_M_ARM',
    '_M_ARM_ARMV7VE',
    '_M_ARM_FP',
    '_M_ARM64',
    '_M_ARM64EC',
    '_M_CEE',
    '_M_CEE_PURE',
    '_M_CEE_SAFE',
    '_M_FP_CONTRACT',
    '_M_FP_EXCEPT',
    '_M_FP_FAST',
    '_M_FP_PRECISE',
    '_M_FP_STRICT',
    '_M_IX86',
    '_M_IX86_FP',
    '_M_X64',
    '_MANAGED',
    '_MSC_BUILD',
    '_MSC_EXTENSIONS',
    '_MSC_FULL_VER',
    '_MSC_VER',
    '_MSVC_LANG',
    '__MSVC_RUNTIME_CHECKS',
    '_MSVC_TRADITIONAL',
    '_MT',
    '_NATIVE_WCHAR_T_DEFINED',
    '_OPENMP',
    '_PREFAST_',
    '__SANITIZE_ADDRESS__',
    '__TIMESTAMP__',
    '_VC_NODEFAULTLIB',
    '_WCHAR_T_DEFINED',
    '_WIN32',
    '_WIN64',
    '_WINRT_DLL',
}

local PRIORITY = {
    x64 = 1,
    arm64 = 2,
    x86 = 3,
    arm = 4,
}

local ARCHS = {
    x64 = 'x86_64',
}

local function test_cl(env, lang, flags)
    local test_file = context.bld_dir:make_node('main_test.' .. lang)
    local test_content
    if lang == 'c' then
        test_content = '#include <stdio.h>\n\n#define show(X) #X X\n'
    else
        test_content = '#include <cstdio>\n\n#define show(X) #X X\n'
    end
    for _, macro in ipairs(MSVC_PREDEFINED_MACROS) do
        test_content = test_content .. '#ifdef ' .. macro .. '\nshow(' .. macro .. ')\n#endif\n'
    end
    local command = env.CL
    for _, flag in ipairs(flags) do
        table.insert(command, flag)
    end
    for _, include in ipairs(env.SYSTEM_INCLUDES) do
        table.insert(command, '/I')
        table.insert(command, include)
    end
    table.insert(command, test_file)
    table.insert(command, '/EP')
    test_file:write(test_content)
    local p = context:popen(command)
    local result, _out, err = p:communicate('')
    if result ~= true then
        context:raise_error('Failed to compile test file:\n' .. tostring(err))
    end
    return result
end

--- Discovers available MSVC compilers.
---
--- @return [string,string,string,Node,string][]
local function vswhere_msvc()
    local compilers = {}
    local vswhere ---@type string
    if context.settings.OS == 'windows' then
        vswhere = 'C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\vswhere.exe'
    else
        vswhere = '/mnt/c/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe'
    end
    local p = context:popen({
        vswhere,
        '-all',
        '-products',
        '*',
        '-find',
        'VC\\Tools\\MSVC',
    })
    local result, out, _err = p:communicate('')
    if result then
        for path in out:lines() do
            local vs_path
            if context.settings.OS == 'windows' then
                vs_path = context.path:make_node(path)
            else
                vs_path = context.path:make_node('/mnt/c/' .. path:sub(4):gsub('\\', '/'))
            end
            paths = context:search(vs_path, '*/bin/*/*/cl.exe')
            for _, cl in ipairs(paths) do
                local target_arch = cl.parent:name():lower()
                local host_arch = cl.parent.parent:name():sub(5):lower()
                local version = cl.parent.parent.parent.parent:name()
                table.insert(compilers, { version, host_arch, target_arch, cl, path })
            end
        end
    end
    table.sort(compilers, function(a, b)
        if a[1] == b[1] then
            if a[2] == b[2] then
                return PRIORITY[a[3]] < PRIORITY[b[3]]
            end
            return PRIORITY[a[2]] < PRIORITY[b[2]]
        end
        return a[1] > b[1]
    end)
    return compilers
end

local function find_windows_sdk()
    local sdk = {}
    local p = context:popen({
        'powershell.exe',
        '-Command',
        '(Get-ItemProperty -Path "HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Microsoft SDKs\\Windows\\v10.0" -Name InstallationFolder).InstallationFolder',
    })
    local result, out, err = p:communicate('')
    if result then
        for path in out:lines() do
            sdk[1] = path
        end
    else
        context:raise_error('Failed to find Windows SDK path:\n' .. tostring(err))
    end
    local p = context:popen({
        'powershell.exe',
        '-Command',
        '(Get-ItemProperty -Path "HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Microsoft SDKs\\Windows\\v10.0" -Name ProductVersion).ProductVersion',
    })
    local result, out, err = p:communicate('')
    if result then
        for version in out:lines() do
            sdk[2] = version
        end
    else
        context:raise_error('Failed to find Windows SDK version:\n' .. tostring(err))
    end
    return sdk
end

local function load_msvc(env, flags, language_flag, lang, var, sdk)
    env[var .. 'FLAGS'] = { '/nologo', '/c', '/external:W1', language_flag }
    env:append(var .. 'FLAGS', flags)
    env[var .. '_COMPILER_NAME'] = 'msvc'
    env[var .. '_DEPENDENCY_TYPE'] = 'msvc'
    env[var .. '_TGT_F'] = '/Fo:'
    env[var .. '_DEFINE_ST'] = '/D'
    env[var .. '_INCLUDE_ST'] = '/I'
    env[var .. '_SYSTEM_INCLUDE_ST'] = { '/external:I' }
    env[var .. '_IDIRAFTER'] = '/I'
    env[var .. 'FLAGS.warn.none'] = { '/W0' }
    env[var .. 'FLAGS.warn.all'] = { '/W4' }

    env.LINK = env.CL[1].parent:make_node('link.exe')
    env.LINKFLAGS = { '/nologo' }
    env.LINK_LIB_F = '%s.lib'
    env.LINK_TGT_F = '/out:%s'
    env.LINKFLAGS_shlib = '/dll'
    env.LINK_LIBPATH_F = '/LIBPATH:%s'

    env.LIB = env.CL[1].parent:make_node('lib.exe')
    env.LIBFLAGS = { '/nologo' }
    env.LIB_TGT_F = '/OUT:%s'

    env.SHLIB_PATTERN = '%s.dll'
    env.STLIB_PATTERN = '%s.lib'
    env.PROGRAM_PATTERN = '%s.exe'

    local sdk_path, sdk_version = table.unpack(sdk)

    local system_includes = {
        env.CL_PATH .. '\\' .. env.CL_VERSION .. '\\' .. 'include',
        sdk_path .. '\\Include\\' .. sdk_version .. '.0\\ucrt',
        sdk_path .. '\\Include\\' .. sdk_version .. '.0\\um',
        sdk_path .. '\\Include\\' .. sdk_version .. '.0\\shared',
    }
    local system_libs = {
        env.CL_PATH .. '\\' .. env.CL_VERSION .. '\\lib\\' .. env.CL_TARGET_ARCH,
        sdk_path .. '\\Lib\\' .. sdk_version .. '.0\\ucrt\\' .. env.CL_TARGET_ARCH,
        sdk_path .. '\\Lib\\' .. sdk_version .. '.0\\um\\' .. env.CL_TARGET_ARCH,
    }
    env.SYSTEM_INCLUDES = system_includes
    env.LIBPATHS = system_libs

    test_cl(env, lang, env[var .. 'FLAGS'])
    context:load_tool('internal/' .. lang)
    context:load_tool('internal/link')
end

function Bolt.MSVC.load_c(flags, sdk)
    local env = context.env
    env.CC = env.CL
    load_msvc(env, flags, '/TC', 'c', 'C', sdk)
end

function Bolt.MSVC.load_cxx(flags, sdk)
    local env = context.env
    env.CXX = env.CL
    load_msvc(env, flags, '/TP', 'c++', 'CXX', sdk)
end

local languages = {
    ['c'] = Bolt.MSVC.load_c,
    ['c++'] = Bolt.MSVC.load_cxx,
}

function Bolt.MSVC.discover(callback, language_flags, global_flags)
    local is_wsl = context.src_dir:make_node('/proc/sys/fs/binfmt_misc/WSLInterop'):is_file()
    local seen = {}
    global_flags = global_flags or {}
    if context.settings.OS == 'windows' or is_wsl then
        context:try('Looking for MSVC compilers', function()
            local sdk = find_windows_sdk()
            local compilers = vswhere_msvc()

            for _, cl in ipairs(compilers) do
                key = cl[1] .. cl[3]
                if not seen[key] then
                    --context:try('testing cl ' .. tostring(cl[4]), function()
                    local env = context:derive()
                    context:with(env, function()
                        env.CL = { cl[4] }
                        env.CL_PATH = cl[5]
                        env:append('CL', global_flags)
                        env.CL_VERSION = cl[1]
                        env.CL_HOST_ARCH = cl[2]
                        env.CL_TARGET_ARCH = cl[3]
                        env.TARGET_OS = 'windows'
                        env.ARCHITECTURE = ARCHS[cl[3]] or cl[3]
                        for lang, flags in pairs(language_flags) do
                            languages[lang](flags, sdk)
                        end
                    end)
                    if callback(env) ~= true then
                        return 'done'
                    end
                    --end)
                    seen[key] = true
                end
            end
            return 'done'
        end)
    end
end
