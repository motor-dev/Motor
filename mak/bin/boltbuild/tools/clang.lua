---@type Context
local context = ...

context:load_tool('compiler_gnu')
context:load_tool('string_ext')

Clang = {}

---@param c_flags (string|Node)[]) The flags to pass to the compiler.
function Clang.load_clang_c(c_flags)
    local env = context.env
    env.CFLAGS = c_flags
    env.C_COMPILER_NAME = 'clang'
    env.C_TGT_F = '-o'
    env.DEFINE_ST = '-I'
    env.INCLUDE_ST = '-I'
    env.SYSTEM_INCLUDE_ST = '-isystem%s'

    local defines = GnuCompiler.get_specs(env.CC, "C")
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

    env.CLANG_C_VERSION = version[1] .. '.' .. version[2] .. '.' .. version[3]
end

---@param cxx_flags (string|Node)[]) The flags to pass to the compiler.
function Clang.load_clang_cxx(cxx_flags)
    local env = context.env
    -- if a  Clang C compiler is loaded, use that
    if env.CC and env.C_COMPILER_NAME == 'clang' then
        env.CXX = env.CC
        env:append('CXX', '-x')
        env:append('CXX', 'c++')
    else
        -- todo
        context:error('Could not find a valid Clang c++ compiler')
    end

    env.CXXFLAGS = cxx_flags
    env.CXX_COMPILER_NAME = 'clang'
    env.CXX_TGT_F = '-o'
    env.DEFINE_ST = '-I'
    env.INCLUDE_ST = '-I'
    env.SYSTEM_INCLUDE_ST = '-isystem%s'

    local defines = GnuCompiler.get_specs(env.CXX, "CXX")
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
    env.CLANG_CXX_VERSION = version[1] .. '.' .. version[2] .. '.' .. version[3]
end

---@param clang Node the path to the Clang executable
---@param c_flags (string|Node)[]? Extra flags that the C compiler should support
---@param cxx_flags (string|Node)[]? Extra flags that the C++ compiler should support
---@return Environment[] An array to store discovered Clang compilers.
function Clang.detect_clang_targets(clang, c_flags, cxx_flags)
    if c_flags == nil then
        c_flags = {}
    end
    if cxx_flags == nil then
        cxx_flags = {}
    end
    local result = {}

    local full_command = { clang }
    for _, arg in ipairs(c_flags) do
        full_command[1 + #full_command] = arg
    end
    full_command[1 + #full_command] = '-x'
    full_command[1 + #full_command] = 'c'
    full_command[1 + #full_command] = '-v'
    full_command[1 + #full_command] = '-E'
    full_command[1 + #full_command] = '-'
    local _, out, err = context:popen(full_command):communicate()

    local search_paths = false
    local paths = {}
    for line in (err + out):lines() do
        line = string.trim(line)
        if string.starts_with(line, "#include <...>") then
            search_paths = true
        elseif string.starts_with(line, "ignoring nonexistent directory \"") then
            local path = context.path:make_node(line:sub(33, -2))
            paths[1+#paths] = path
        elseif search_paths and string.starts_with(line, "End of search list") then
            break
        elseif search_paths then
            local path = context.path:make_node(line)
            paths[1+#paths] = path
        end
    end

    local seen = {}
    for _, path in ipairs(paths) do
        local component = path:name()
        local relpath = ''
        local component_count = 1
        while component do
            path = path.parent
            local component_list = string.split(component, '-')
            if #component_list >= 2 then
                for _, triple in ipairs(context:search(path, '*-*/'..relpath..'/sys', true)) do
                    for i = 1, component_count do
                        triple = triple.parent
                    end
                    triple = triple:name()
                    if seen[triple] == nil then
                        seen[triple] = triple
                        if context:try('running clang ' .. clang:abs_path() .. ' for target ' .. triple, function()
                            context:with(context:derive(), function()
                                local c_target_flags = {}
                                local cxx_target_flags = {}
                                for _, f in ipairs(c_flags) do
                                    c_target_flags[1 + #c_target_flags] = f
                                end
                                for _, f in ipairs(cxx_flags) do
                                    cxx_target_flags[1 + #cxx_target_flags] = f
                                end
                                c_target_flags[1+ #c_target_flags] = '-target'
                                c_target_flags[1+ #c_target_flags] = triple
                                cxx_target_flags[1+ #cxx_target_flags] = '-target'
                                cxx_target_flags[1+ #cxx_target_flags] = triple
                                context.env.CC = { clang }
                                Clang.load_clang_c(c_target_flags)
                                Clang.load_clang_cxx(cxx_target_flags)
                                result[1 + #result] = context.env
                            end)
                        end) then
                            break
                        end
                    end
                end
            end
            relpath = component..'/'..relpath
            component_count = component_count + 1
            component = path:name()
        end
    end
    return result
end

---Discover as many Clang compilers as possible, including extra triples where applicable. When clang compilers are found,
---load the compiler in a new environment derived from the current environment.
---@param c_flags (string|Node)[]? Extra flags that the C compiler should support
---@param cxx_flags (string|Node)[]? Extra flags that the C++ compiler should support
---@return Environment[] A list of environments where a Clang compiler has been loaded.
function Clang.discover(c_flags, cxx_flags)
    local result = {}
    context:try('Looking for Clang compilers', function()
        ---@type table<string, Node>
        local seen = {}
        local paths = context.settings.path

        for _, path in ipairs(--[[---@type Node[] ]] paths) do
            for _, node in ipairs(context:search(path, 'clang*' .. context.settings.exe_suffix)) do
                local version = string.match(node:name(), "^clang%-?(%d*)" .. context.settings.exe_suffix .. "$")
                if version ~= nil then
                    if node:is_file() then
                        node = node:read_link()
                        local absolute_path = node:abs_path()
                        if seen[absolute_path] == nil then
                            seen[absolute_path] = node
                            for _, env in ipairs(Clang.detect_clang_targets(node, c_flags, cxx_flags)) do
                                env.CLANG_VERSION = version
                                result[1 + #result] = env
                            end
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
