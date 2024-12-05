---@type Context
local context = ...

context:load_tool('internal/module_core')
context:load_tool('internal/module_process')

---@param module Module
---@param source_file SourceFile
---@param category string?
local function make_build_node(module, source_file, category)
    category = category or 'obj'
    local directory = context.bld_dir
    directory = directory:make_node(module.group)
    directory = directory:make_node(module.target)
    directory = directory:make_node(category)
    local target_node = directory:make_node(source_file.full_path:path_from(source_file.base_path))
    target_node = target_node:change_ext("o")
    return target_node, directory
end

---@param module Module
local function prepare(module)
    module.target = module.name:gsub("%?<>:%*|%\"", "-")
    module.compiled_tasks = {}
    module.make_build_node = make_build_node
end

---@param module Module
---@param dependency Module
---@param seen table<Module,boolean>
---@param add_objects boolean
local function process_link(module, dependency, seen, add_objects)
    local already_seen, already_added_objects = table.unpack(seen[dependency] or { false, false })
    if not already_seen or (not already_added_objects and add_objects) then
        seen[dependency] = { true, add_objects }
        if add_objects then
            for _, object in ipairs(dependency.objects) do
                table.insert(module.objects, object)
            end
        end
        if not already_seen then
            module.env:append('LIBS', dependency.public_flags.LIBS or {})
            module.env:append('LIBPATHS', dependency.public_flags.LIBPATHS or {})
            module.env:append('LINKFLAGS', dependency.public_flags.LINKFLAGS or {})
        end
        if dependency:has_property('link_task') then
            table.insert(module.dep_link_tasks, dependency.link_task)
        end
        for _, dep in ipairs(dependency.public_dependencies) do
            process_link(module, dep, seen, add_objects and not dep:has_property('link_task'))
        end
        if add_objects then
            for _, dep in ipairs(dependency.internal_dependencies) do
                process_link(module, dep, seen, not dep:has_property('link_task'))
            end
        end
    end
end

---@param module Module
---@param dependency Module
---@param seen table<Module,boolean>
local function process_dependency(module, dependency, seen)
    if not seen[dependency] then
        seen[dependency] = true
        for _, include in ipairs(dependency.public_includes) do
            table.insert(module.internal_includes, include)
        end
        for _, define in ipairs(dependency.public_defines) do
            table.insert(module.internal_defines, define)
        end
        for flag_name, values in pairs(dependency.public_flags) do
            module.env:append(flag_name, values)
        end
        for _, dep in ipairs(dependency.public_dependencies) do
            process_dependency(module, dep, seen)
        end
    end
end

---@param module Module
local function process_dependencies(module)
    local seen = { }
    local add_objects = false
    for _, feature in ipairs(module.features) do
        if feature == 'program' then
            add_objects = true
        elseif feature == 'shlib' then
            add_objects = true
        elseif feature == 'stlib' then
            add_objects = true
        end
    end

    for _, dependency in ipairs(module.internal_dependencies) do
        context:post(dependency)
        process_dependency(module, dependency, seen)
    end
    for _, dependency in ipairs(module.public_dependencies) do
        context:post(dependency)
        process_dependency(module, dependency, seen)
    end

    if add_objects then
        seen = { }
        for _, dependency in ipairs(module.internal_dependencies) do
            process_link(module, dependency, seen, not dependency:has_property('link_task'))
        end
        for _, dependency in ipairs(module.public_dependencies) do
            process_link(module, dependency, seen, not dependency:has_property('link_task'))
        end
    end
end

---@param module Module
local function process_flags(module)
    for _, include in ipairs(module.internal_includes) do
        module.env:append('INCLUDES', include:abs_path())
    end
    for _, include in ipairs(module.public_includes) do
        module.env:append('INCLUDES', include:abs_path())
    end
    for _, define in ipairs(module.internal_defines) do
        if define[2] then
            module.env:append('DEFINES', define[1] .. '=' .. define[2])
        else
            module.env:append('DEFINES', define[1])
        end
    end
    for _, define in ipairs(module.public_defines) do
        if define[2] then
            module.env:append('DEFINES', define[1] .. '=' .. define[2])
        else
            module.env:append('DEFINES', define[1])
        end
    end
end

---@param module Module
local function process_source(module)
    for _, source_info in ipairs(module.source_patterns) do
        local path = source_info.path
        for _, source in ipairs(context:search(path, source_info.pattern)) do
            if module.source_filter({ base_path = path, full_path = source }, module.env) then
                local ext = source:extension()
                local source_processor = Bolt.Module.extension_registry[ext]
                if source_processor == nil then
                    context:raise_error("No tool that can handle file " .. tostring(source) .. " with extension " .. ext .. ".")
                end
                source_processor(module, { base_path = path, full_path = source })
            end
        end
    end

    for _, source_info in ipairs(module.source) do
        if module.source_filter(source_info, module.env) then
            local ext = source_info.full_path:extension()
            local source_processor = Bolt.Module.extension_registry[ext]
            if source_processor == nil then
                context:raise_error("No tool that can handle file " .. tostring(source_info.full_path) .. " with extension " .. ext .. ".")
            end
            source_processor(module, source_info)
        end
    end
end

---@param module Module
local function process_link_program(module)
    if #module.objects ~= 0 then
        local target_node = context.bld_dir
        target_node = target_node:make_node(module.group)
        target_node = target_node:make_node(module.target)
        target_node = target_node:make_node(string.format(context.env.PROGRAM_PATTERN, module.target))
        local link_task = module:declare_task("program", {}, { target_node })
        for _, task in ipairs(module.compiled_tasks) do
            link_task:add_input(task.outputs[1])
        end
        for _, node in ipairs(module.env.OBJECTS) do
            link_task:add_input(node)
        end

        module.link_task = link_task
    end
end

---@param module Module
local function process_link_shlib(module)
    if #module.objects ~= 0 then
        local target_node = context.bld_dir
        target_node = target_node:make_node(module.group)
        target_node = target_node:make_node(module.target)
        target_node = target_node:make_node(string.format(context.env.SHLIB_PATTERN, module.target))
        local link_task = module:declare_task("shlib", {}, { target_node })
        for _, object in ipairs(module.objects) do
            link_task:add_input(object)
        end
        module.link_task = link_task
        for _, link_dep in ipairs(module.dep_link_tasks) do
            link_task:set_run_after(link_dep)
        end
        if module.public_flags.LIBS then
            table.insert(module.public_flags.LIBS, module.target)
        else
            module.public_flags.LIBS = { module.target }
        end
        if module.public_flags.LIBPATHS then
            table.insert(module.public_flags.LIBPATHS, target_node.parent)
        else
            module.public_flags.LIBPATHS = { target_node.parent }
        end
    end
end

---@param module Module
local function process_link_stlib(module)
    if #module.objects ~= 0 then
        local target_node = context.bld_dir
        target_node = target_node:make_node(module.group)
        target_node = target_node:make_node(module.target)
        target_node = target_node:make_node(string.format(context.env.STLIB_PATTERN, module.target))
        local link_task = module:declare_task("stlib", {}, { target_node })
        for _, task in ipairs(module.compiled_tasks) do
            link_task:add_input(task.outputs[1])
        end
        module.link_task = link_task
    end
end

context
        :feature('module', 'prepare', prepare)
context
        :feature('module', 'process_dependencies', process_dependencies)
        :set_run_after({ "prepare" })
context
        :feature('module', 'process_flags', process_flags)
        :set_run_after({ "process_dependencies" })
context
        :feature('module', 'process_source', process_source)
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
