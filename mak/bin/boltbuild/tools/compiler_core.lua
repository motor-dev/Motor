---@type Context
local context = ...

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
    for _, dependency_name in ipairs(generator.dependencies) do
        local dependency = context:get_generator_by_name(dependency_name)
        context:post(dependency)
    end
end

---@param generator Generator
local function process_flags(generator)
end

---@param generator Generator
local function process_source(generator)
    for _, source in ipairs(generator.source) do
        local ext = source:extension()
        local source_processor = context._extensions[ext]
        if source_processor == nil then
            context:fatal("No tool that can handle files with extension "..ext..".")
        end
        source_processor(generator, source)
    end
end

---@param generator Generator
local function process_link_program(generator)
    local target_node = context.bld_dir
    target_node = target_node:make_node(generator.group)
    target_node = target_node:make_node(generator.target)
    target_node = target_node:make_node(string.format(context.env.PROGRAM_PATTERN, generator.target))
    local link_task = generator("program", {}, {target_node})
    for _, task in ipairs(generator.compiled_tasks) do
        link_task:add_input(task.outputs[1])
    end
    generator.link_task = link_task
end

---@param generator Generator
local function process_link_shlib(generator)
    local target_node = context.bld_dir
    target_node = target_node:make_node(generator.group)
    target_node = target_node:make_node(generator.target)
    target_node = target_node:make_node(string.format(context.env.SHLIB_PATTERN, generator.target))
    local link_task = generator("shlib", {}, {target_node})
    for _, task in ipairs(generator.compiled_tasks) do
        link_task:add_input(task.outputs[1])
    end
    generator.link_task = link_task
end

---@param generator Generator
local function process_link_stlib(generator)
    local target_node = context.bld_dir
    target_node = target_node:make_node(generator.group)
    target_node = target_node:make_node(generator.target)
    target_node = target_node:make_node(string.format(context.env.STLIB_PATTERN, generator.target))
    local link_task = generator("stlib", {}, {target_node})
    for _, task in ipairs(generator.compiled_tasks) do
        link_task:add_input(task.outputs[1])
    end
    generator.link_task = link_task
end




context
        :feature('c,cxx', 'prepare', prepare)
context
        :feature('c,cxx', 'process_dependencies', process_dependencies)
        :set_run_after({"prepare"})
context
        :feature('c,cxx', 'process_flags', process_flags)
        :set_run_after({"process_dependencies"})
context
        :feature('c,cxx', 'process_source', process_source)
        :set_run_after({"process_flags"})

context
        :feature('program', 'process_link_program', process_link_program)
        :set_run_after({"process_source"})
context
        :feature('shlib', 'process_link_shlib', process_link_shlib)
        :set_run_after({"process_source"})
context
        :feature('stlib', 'process_link_stlib', process_link_stlib)
        :set_run_after({"process_source"})

context:command_driver('shlib', 'yellow', '${LINK} ${LINKFLAGS} ${LINK_SRC_FLAG:SRC} ${LIB_TGT_F:TGT[0]}')
context:command_driver('stlib', 'yellow', '${LIB} ${LIBFLAGS} ${LIB_SRC_FLAG:SRC} ${LIB_TGT_F:TGT[0]}')
context:command_driver('program', 'yellow', '${LINK} ${LINKFLAGS} ${LINK_SRC_FLAG:SRC} ${LIB_TGT_F:TGT[0]}')
