local context = ...

local function detect_clang_target(node, arch, target)
    local handle = context:popen({ node, '-x', 'c++', '--std', 'c++14', '-v', '-E', '-target', target, '-' })
    local success, out, err = handle:communicate("#include <cstdio>")
    if success then
        context.compilers[1 + #context.compilers] = table.pack('clang', node, arch, target)
    end
end

local function detect_clang(node)
    local _, out, err = context:popen({ node, '-x', 'c++', '-v', '-E', '-' }):communicate()
    local search_paths = false
    for line in (err .. out):lines() do
        if line:trim():starts_with("#include <...>") then
            search_paths = true
        elseif search_paths and line:trim():starts_with("End of search list") then
            break
        elseif search_paths then
            local path = context.path:make_node(line:trim())
            local component = path:name()
            while component do
                path = path.parent
                component = component:split('-')
                if #component >= 2 and context.ARCHS[component[1]] then
                    for _, triple in ipairs(context:search(path, '*-*')) do
                        triple = triple:name()
                        local arch = context.ARCHS[triple:split('-')[1]]
                        if arch then
                            context:try('running clang ' .. node:abspath(), function()
                                detect_clang_target(node, arch, triple)
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
    local seen = {}
    for _, path in ipairs(context.settings.path) do
        path = path.parent:make_node('lib')
        for _, node in ipairs(context:search(path, 'llvm*/bin/clang' .. context.settings.exe_suffix)) do
            local absolute_path = node:abspath()
            if seen[absolute_path] == nil then
                seen[absolute_path] = node
                pcall(detect_clang, node)
            end
        end
    end

    return 'done'
end)