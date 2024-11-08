---@type Context
local context = ...

context:load_tool('string_ext')
context._extensions = {}

---Register a function that processes an extension
---@param extensions string|string[] an extension, comma-separated extensions or a list of extensions
---@param callback function(task_gen: Generator, node:Node) a function that will be called for every file that matches one of the extensions
function context:extension(extensions, callback)
    if type(extensions) == "string" then
        extensions = extensions:split(',')
    end
    for _, ext in ipairs(extensions) do
        context._extensions[ext] = callback
    end
end

---@param generator Generator
---@param node Node
local function make_build_node(generator, node)
    local target_node = context.bld_dir
    target_node = target_node:make_node(generator.group)
    target_node = target_node:make_node(generator.target)
    target_node = target_node:make_node(node:path_from(context.src_dir))
    target_node = target_node:change_ext("o")
    return target_node
end

---@param generator Generator
local function prepare(generator)
    generator.target = generator.name:gsub("%?<>:%*|%\"", "-")
    generator.compiled_tasks = {}
    generator.make_build_node = make_build_node
end

---@param generator Generator
local function process_dependencies(generator)
    for _, dependency in ipairs(generator.dependencies) do
        context:post(dependency)
        for _, include in ipairs(dependency.public_includes) do
            generator.public_includes[1 + #generator.public_includes] = include
        end
        for _, define in ipairs(dependency.public_defines) do
            generator.public_defines[1 + #generator.public_defines] = define
        end
    end
    for _, dependency in ipairs(generator.public_dependencies) do
        context:post(dependency)
        for _, include in ipairs(dependency.public_includes) do
            generator.public_includes[1 + #generator.public_includes] = include
        end
        for _, define in ipairs(dependency.public_defines) do
            generator.public_defines[1 + #generator.public_defines] = define
        end
    end
end

---@param generator Generator
local function process_flags(generator)
    for _, include in ipairs(generator.includes) do
        generator.env:append('INCLUDES', include:abs_path())
    end
    for _, include in ipairs(generator.public_includes) do
        generator.env:append('INCLUDES', include:abs_path())
    end
    for _, define in ipairs(generator.defines) do
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
    for _, pattern in ipairs(generator.source) do
        for _, source in ipairs(context:search(generator.path, pattern)) do
            local ext = source:extension()
            local source_processor = context._extensions[ext]
            if source_processor == nil then
                context:fatal("No tool that can handle file " .. tostring(source) .. " with extension " .. ext .. ".")
            end
            source_processor(generator, source)
        end
    end
end

---@param generator Generator
local function process_link_program(generator)
    if generator.objects then
        local target_node = context.bld_dir
        target_node = target_node:make_node(generator.group)
        target_node = target_node:make_node(generator.target)
        target_node = target_node:make_node(string.format(context.env.PROGRAM_PATTERN, generator.target))
        local link_task = generator("program", {}, { target_node })
        for _, task in ipairs(generator.compiled_tasks) do
            link_task:add_input(task.outputs[1])
        end
        generator.link_task = link_task
    end
end

---@param generator Generator
local function process_link_shlib(generator)
    if generator.objects then
        local target_node = context.bld_dir
        target_node = target_node:make_node(generator.group)
        target_node = target_node:make_node(generator.target)
        target_node = target_node:make_node(string.format(context.env.SHLIB_PATTERN, generator.target))
        local link_task = generator("shlib", {}, { target_node })
        for _, task in ipairs(generator.compiled_tasks) do
            link_task:add_input(task.outputs[1])
        end
        generator.link_task = link_task
    end
end

---@param generator Generator
local function process_link_stlib(generator)
    if generator.objects then
        local target_node = context.bld_dir
        target_node = target_node:make_node(generator.group)
        target_node = target_node:make_node(generator.target)
        target_node = target_node:make_node(string.format(context.env.STLIB_PATTERN, generator.target))
        local link_task = generator("stlib", {}, { target_node })
        for _, task in ipairs(generator.compiled_tasks) do
            link_task:add_input(task.outputs[1])
        end
        generator.link_task = link_task
    end
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

context:command_driver('shlib', 'yellow', '${LINK} ${LINKFLAGS} ${LINKFLAGS_shlib} ${LINK_SRC_F:SRC} ${LIB_TGT_F:TGT[0]} ${LINK_LIBPATH_F:LIBPATHS} ${LINK_LIB_F:LIBS}')
context:command_driver('program', 'yellow', '${LINK} ${LINKFLAGS} ${LINKFLAGS_program} ${LINK_SRC_F:SRC} ${LIB_TGT_F:TGT[0]}')
context:command_driver('stlib', 'yellow', '${LIB} ${LIBFLAGS} ${LINK_SRC_F:SRC} ${LIB_TGT_F:TGT[0]} ${LINK_LIBPATH_F:LIBPATHS} ${LINK_LIBS_F:LIBS}')
