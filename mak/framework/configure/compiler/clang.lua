---@type(Context)
local context = ...

local function detect_clang_target(node, arch, target)
    local handle = context:popen({ node, '-x', 'c++', '--std', 'c++14', '-v', '-dM', '-E', '-target', target, '-' })
    local success, out, err = handle:communicate()
    if success then
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
        context.compilers[1 + #context.compilers] = table.pack('clang', node, arch, target, version, includes, defines)
    end
end

local function detect_clang(node)
    local _, out, err = context:popen({ node, '-x', 'c++', '-v', '-E', '-' }):communicate()
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
                            context:try('running clang ' .. node:abs_path(), function()
                                detect_clang_target(node, arch, triple:name())
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

context:try('Looking for Clang compilers', function()
    ---@type table<string, Node>
    local seen = {}
    for _, path in ipairs(--[[---@type Node[] ]] context.settings.path) do
        path = path.parent:make_node('lib')
        for _, node in ipairs(context:search(path, 'llvm*/bin/clang' .. context.settings.exe_suffix)) do
            local absolute_path = node:abs_path()
            if seen[absolute_path] == nil then
                seen[absolute_path] = node
                pcall(detect_clang, node)
            end
        end
    end

    return 'done'
end)