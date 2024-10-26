---@type Context
local context = ...

Clang = {}

---Add defaul Clang flags into the environment
function Clang.configure()
    context.env.COMPILER = 'clang'
    context.env.CXX_TGT_F = '-o'

    context.env.DEFINE_ST = '-I'
    context.env.INCLUDE_ST = '-I'
    context.env.SYSTEM_INCLUDE_ST = '-isystem%s'
end

---@param clang_command string|Node[]
---@param arch string
---@param target string
---@return Environment a new environment, derived from the current context environment, with Clang setup.
function Clang.detect_clang_target(clang_command, arch, target)
    local full_command = {}
    for i, arg in ipairs(clang_command) do
        full_command[i] = arg
    end
    full_command[1 + #full_command] = '-x'
    full_command[1 + #full_command] = 'c++'
    full_command[1 + #full_command] = '-v'
    full_command[1 + #full_command] = '-dM'
    full_command[1 + #full_command] = '-E'
    full_command[1 + #full_command] = '-target'
    full_command[1 + #full_command] = target
    full_command[1 + #full_command] = '-'
    local handle = context:popen(full_command)
    local success, out, err = handle:communicate()
    if not success then
        error(err)
    end

    return context:with(context:derive(), function()
        context.env.CC = clang_command
        context.env.CXX = clang_command
        Clang.configure()

        ---@type table<string, string>
        local defines = {}
        ---@type Node[]
        local includes = {}
        local version = { 0, 0, 0 }
        local search_paths = false

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
            elseif line:find('__clang_major__') then
                local s, _, v = line:find('__clang_major__%s+(%d+)')
                if s then
                    version[1] = tonumber(v)
                end
            elseif line:find('__clang_minor__') then
                local s, _, v = line:find('__clang_minor__%s+(%d+)')
                if s then
                    version[2] = tonumber(v)
                end
            elseif line:find('__clang_patchlevel__') then
                local s, _, v = line:find('__clang_patchlevel__%s+(%d+)')
                if s then
                    version[3] = tonumber(v)
                end
            else
                local s, _, name, value = line:find('%s*#define%s+([%w_]+)%s*(.*)')
                if s then
                    defines[tostring(name)] = tostring(value)
                end
            end
        end

        local node = clang_command[1]
        context.compilers[1 + #context.compilers] = context.Compiler:new {
            name = 'clang',
            arch = arch,
            target = target,
            version = version[1] .. '.' .. version[2] .. '.' .. version[3],
            command_c = { node, '-x', 'c', '-target', target },
            command_cxx = { node, '-x', 'c++', '-target', target },
            setup = function()
                context.env.CC = { node, '-x', 'c', '-target', target }
                context.env.CXX = { node, '-x', 'c++', '-target', target }
                context:load_tool('clang', true)
            end
        }
        return context.env
    end)
end

---@param clang_command (string|Node)[] The clang command to run.
---@param result Environment[] An array to store discovered Clang compilers.
function Clang.detect_clang_targets(clang_command, result)
    local full_command = {}
    for i, arg in ipairs(clang_command) do
        full_command[i] = arg
    end
    full_command[1 + #full_command] = '-x'
    full_command[1 + #full_command] = 'c++'
    full_command[1 + #full_command] = '-v'
    full_command[1 + #full_command] = '-E'
    full_command[1 + #full_command] = '-'
    local _, out, err = context:popen(full_command):communicate()

    local search_paths = false
    local seen = {}
    for line in (err + out):lines() do
        line = string.trim(line)
        if string.starts_with(line, "#include <...>") then
            search_paths = true
        elseif search_paths and string.starts_with(line, "End of search list") then
            break
        elseif search_paths then
            local path = context.path:make_node(line)
            local component = path:name()
            while component do
                path = path.parent
                local component_list = string.split(component, '-')
                if #component_list >= 2 and context.ARCHITECTURES[component_list[1]] then
                    for _, triple in ipairs(context:search(path, '*-*')) do
                        local triple_components = string.split(triple:name(), '-')
                        local arch = context.ARCHITECTURES[triple_components[1]]
                        if arch and seen[arch] == nil then
                            seen[arch] = arch
                            context:try('running clang ' .. clang_command[1]:abs_path(), function()
                                result[1 + #result] = Clang.detect_clang_target(clang_command, arch, triple:name())
                            end)
                        end
                    end
                    break
                end
                component = path:name()
            end
        end
    end
end

---Discover as many Clang compilers as possible, including extra triples where applicable. When clang compilers are found,
---load the compiler in a new environment derived from the current environment.
---@param flags (string|Node)[] Extra flags that the compiler should support
---@return Environment[] A list of environments where a Clang compiler has been loaded.
function Clang.discover(flags)
    if flags == nil then
        flags = {}
    end
    local result = {}
    context:try('Looking for Clang compilers', function()
        ---@type table<string, Node>
        local seen = {}
        for _, path in ipairs(--[[---@type Node[] ]] context.settings.path) do
            for _, node in ipairs(context:search(path, 'clang*' .. context.settings.exe_suffix)) do
                if string.match(node:name(), "^clang%-?%d*" .. context.settings.exe_suffix .. "$") then
                    node = node:read_link()
                    local absolute_path = node:abs_path()
                    if seen[absolute_path] == nil then
                        seen[absolute_path] = node
                        local command = { node }
                        for i, arg in ipairs(flags) do
                            command[i + 1] = arg
                        end
                        Clang.detect_clang_targets(command, result)
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
