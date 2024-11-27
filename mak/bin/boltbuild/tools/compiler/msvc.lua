---@type Context
local context = ...

BoltMsvc = {}

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

local function vswhere_msvc()
    local compilers = {}
    local p = context:popen({
        'C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\vswhere.exe',
        '-all',
        '-products',
        '*',
        '-find',
        'VC\\Tools\\MSVC',
    })
    local result, out, err = p:communicate('')
    if result then
        for path in out:lines() do
            path = context.path:make_node(path)
            paths = context:search(path, '*/bin/*/*/cl.exe')
            for _, cl in ipairs(paths) do
                table.insert(compilers, cl)
            end
        end
    end
    return compilers
end

function BoltMsvc.discover(callback, language_flags, global_flags)
    if context.settings.OS == 'windows' then
        context:try('Looking for Msvc compilers', function()
            local seen = {}
            local compilers = vswhere_msvc()

            for _, cl in ipairs(compilers) do
                context:try('Checking ' .. tostring(cl), function()
                    p = context:popen({ cl, })
                end)
            end
            return 'done'
        end)
    end
end
