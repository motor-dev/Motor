---@type Context
local context = ...

context:load_tool('internal/product_core')
context:load_tool('internal/product_process')

---@param generator Generator
---@param node Node
---@param path Node
---@param category string|nil
local function make_build_node(generator, node, path, category)
    category = category or 'obj'
    local directory = context.bld_dir
    directory = directory:make_node(generator.group)
    directory = directory:make_node(generator.target)
    directory = directory:make_node(category)
    local target_node = directory:make_node(node:path_from(path))
    target_node = target_node:change_ext("o")
    return target_node, directory
end

---@param generator Generator
local function prepare(generator)
    generator.target = generator.name:gsub("%?<>:%*|%\"", "-")
    generator.compiled_tasks = {}
    generator.make_build_node = make_build_node
end

---@param generator Generator
---@param dependency Generator
---@param seen table<Generator,boolean>
---@param add_objects boolean
local function process_link(generator, dependency, seen, add_objects)
    local already_seen, already_added_objects = table.unpack(seen[dependency] or { false, false })
    if not already_seen or (not already_added_objects and add_objects) then
        seen[dependency] = { true, add_objects }
        if add_objects then
            for _, object in ipairs(dependency.objects) do
                table.insert(generator.objects, object)
            end
        end
        if not already_seen then
            generator.env:append('LIBS', dependency.libs)
            generator.env:append('LIBPATHS', dependency.libpaths)
            generator.env:append('LINKFLAGS', dependency.linkflags)
        end
        for _, dep in ipairs(dependency.public_dependencies) do
            process_link(generator, dep, seen, add_objects and not dep:has_property('link_task'))
        end
        if add_objects then
            for _, dep in ipairs(dependency.internal_dependencies) do
                process_link(generator, dep, seen, not dep:has_property('link_task'))
            end
        end
    end
end

---@param generator Generator
---@param dependency Generator
---@param seen table<Generator,boolean>
local function process_dependency(generator, dependency, seen)
    if not seen[dependency] then
        seen[dependency] = true
        for _, include in ipairs(dependency.public_includes) do
            table.insert(generator.internal_includes, include)
        end
        for _, define in ipairs(dependency.public_defines) do
            table.insert(generator.internal_defines, define)
        end
        for _, flags in ipairs(dependency.public_flags) do
            local flag_name, values = flags[1], flags[2]
            if values and #values ~= 0 then
                generator.env:append(flag_name, table.unpack(values))
            end
        end
        for _, dep in ipairs(dependency.public_dependencies) do
            process_dependency(generator, dep, seen)
        end
    end
end

---@param generator Generator
local function process_dependencies(generator)
    local seen = { }
    local add_objects = false
    for _, feature in ipairs(generator.features) do
        if feature == 'program' then
            add_objects = true
        elseif feature == 'shlib' then
            add_objects = true
        elseif feature == 'stlib' then
            add_objects = true
        end
    end

    for _, dependency in ipairs(generator.internal_dependencies) do
        context:post(dependency)
        process_dependency(generator, dependency, seen)
    end
    for _, dependency in ipairs(generator.public_dependencies) do
        context:post(dependency)
        process_dependency(generator, dependency, seen)
    end

    if add_objects then
        seen = { }
        for _, dependency in ipairs(generator.internal_dependencies) do
            process_link(generator, dependency, seen, not dependency:has_property('link_task'))
        end
        for _, dependency in ipairs(generator.public_dependencies) do
            process_link(generator, dependency, seen, not dependency:has_property('link_task'))
        end
    end
end

---@param generator Generator
local function process_flags(generator)
    for _, include in ipairs(generator.internal_includes) do
        generator.env:append('INCLUDES', include:abs_path())
    end
    for _, include in ipairs(generator.public_includes) do
        generator.env:append('INCLUDES', include:abs_path())
    end
    for _, define in ipairs(generator.internal_defines) do
        if define[2] then
            generator.env:append('DEFINES', define[1] .. '=' .. define[2])
        else
            generator.env:append('DEFINES', define[1])
        end
    end
    for _, define in ipairs(generator.public_defines) do
        if define[2] then
            generator.env:append('DEFINES', define[1] .. '=' .. define[2])
        else
            generator.env:append('DEFINES', define[1])
        end
    end
end

---@param generator Generator
local function process_source(generator)
    for _, source_info in ipairs(generator.source_patterns) do
        local path, pattern = source_info[1], source_info[2]
        for _, source in ipairs(context:search(path, pattern)) do
            if generator.source_filter(source, path, generator.env) then
                local ext = source:extension()
                local source_processor = context._extensions[ext]
                if source_processor == nil then
                    context:raise_error("No tool that can handle file " .. tostring(source) .. " with extension " .. ext .. ".")
                end
                source_processor(generator, source, path)
            end
        end
    end

    for _, source_info in ipairs(generator.source) do
        local path, source = source_info[1], source_info[2]
        if generator.source_filter(source, path, generator.env) then
            local ext = source:extension()
            local source_processor = context._extensions[ext]
            if source_processor == nil then
                context:raise_error("No tool that can handle file " .. tostring(source) .. " with extension " .. ext .. ".")
            end
            source_processor(generator, source, path)
        end
    end
end

---@param generator Generator
local function process_link_program(generator)
    if #generator.objects ~= 0 then
        local target_node = context.bld_dir
        target_node = target_node:make_node(generator.group)
        target_node = target_node:make_node(generator.target)
        target_node = target_node:make_node(string.format(context.env.PROGRAM_PATTERN, generator.target))
        local link_task = generator:declare_task("program", {}, { target_node })
        for _, task in ipairs(generator.compiled_tasks) do
            link_task:add_input(task.outputs[1])
        end
        for _, node in ipairs(generator.env.OBJECTS) do
            link_task:add_input(node)
        end

        generator.link_task = link_task
    end
end

---@param generator Generator
local function process_link_shlib(generator)
    if #generator.objects ~= 0 then
        local target_node = context.bld_dir
        target_node = target_node:make_node(generator.group)
        target_node = target_node:make_node(generator.target)
        target_node = target_node:make_node(string.format(context.env.SHLIB_PATTERN, generator.target))
        local link_task = generator:declare_task("shlib", {}, { target_node })
        for _, object in ipairs(generator.objects) do
            link_task:add_input(object)
        end
        generator.link_task = link_task
    end
end

---@param generator Generator
local function process_link_stlib(generator)
    if #generator.objects ~= 0 then
        local target_node = context.bld_dir
        target_node = target_node:make_node(generator.group)
        target_node = target_node:make_node(generator.target)
        target_node = target_node:make_node(string.format(context.env.STLIB_PATTERN, generator.target))
        local link_task = generator:declare_task("stlib", {}, { target_node })
        for _, task in ipairs(generator.compiled_tasks) do
            link_task:add_input(task.outputs[1])
        end
        generator.link_task = link_task
    end
end

---@param generator Generator
local function process_link_objects(generator)
end

context
        :feature('c,cxx', 'prepare', prepare)
context
        :feature('c,cxx', 'process_dependencies', process_dependencies)
        :set_run_after({ "prepare" })
context
        :feature('c,cxx', 'process_flags', process_flags)
        :set_run_after({ "process_dependencies" })
context
        :feature('c,cxx', 'process_source', process_source)
        :set_run_after({ "process_flags" })

context
        :feature('program', 'process_link_program', process_link_program)
        :set_run_after({ "process_source" })
context
        :feature('shlib', 'process_link_shlib', process_link_shlib)
        :set_run_after({ "process_source" })
context
        :feature('stlib', 'process_link_stlib', process_link_stlib)
        :set_run_after({ "process_source" })
