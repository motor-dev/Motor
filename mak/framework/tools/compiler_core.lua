---@type Context
local context = ...

context._extensions = {}

---Register a function that processes an extension
---@param extensions string|string[] an extension, comma-separated extensions or a list of extensions
---@param callback function(task_gen: Generator, node:Node) a function that will be called for every file that matches one of the extensions
function context:extension(extensions, callback)
    if type(extensions) == string then
        extensions = string.split(extensions, ',')
    end
    for _, ext in ipairs(extensions) do
        context._extensions[ext] = callback
    end
end

context:feature('c,cxx', 'process_dependencies', function(generator)
    for _, dependency_name in ipairs(generator.dependencies) do
        local dependency = context:get_generator_by_name(dependency_name)
        context:post(dependency)
    end
end)

context:feature('c,cxx', 'process_flags', function(generator)
end, {"process_dependencies"})

context:feature('c,cxx', 'process_source', function(generator)
end)

context:feature('program', 'process_link_program', function(generator)
end)

context:feature('shlib', 'process_link_shlib', function(generator)
end)

context:feature('stlib', 'process_link_stlib', function(generator)
end)
