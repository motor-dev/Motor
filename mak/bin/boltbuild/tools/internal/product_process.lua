---@type Context
local context = ...

context:load_tool('internal/product_core')
context:load_tool('internal/product_process')

---@param generator Generator
---@param node Node
---@param path Node
local function make_build_node(generator, node, path)
    local target_node = context.bld_dir
    target_node = target_node:make_node(generator.group)
    target_node = target_node:make_node(generator.target)
    target_node = target_node:make_node(node:path_from(path))
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
---@param dependency Generator
---@param seen table<Generator,boolean>
local function process_dependency(generator, dependency, seen)
    if not seen[dependency] then
        seen[dependency] = true
        context:post(dependency)
        for _, include in ipairs(dependency.public_includes) do
            generator.includes[1 + #generator.includes] = include
        end
        for _, define in ipairs(dependency.public_defines) do
            generator.defines[1 + #generator.defines] = define
        end
        for _, dep in ipairs(dependency.public_dependencies) do
            process_dependency(generator, dep, seen)
        end
    end
end

---@param generator Generator
local function process_dependencies(generator)
    local seen = { }
    for _, dependency in ipairs(generator.public_dependencies) do
        process_dependency(generator, dependency, seen)
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
    for _, source_info in ipairs(generator.source) do
        local path, pattern = source_info[1], source_info[2]
        for _, source in ipairs(context:search(path, pattern)) do
            if generator.source_filter(source, path, generator.env) then
                local ext = source:extension()
                local source_processor = context._extensions[ext]
                if source_processor == nil then
                    context:fatal("No tool that can handle file " .. tostring(source) .. " with extension " .. ext .. ".")
                end
                source_processor(generator, source, path)
            end
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
        local link_task = generator("program", {}, { target_node })
        for _, task in ipairs(generator.compiled_tasks) do
            link_task:add_input(task.outputs[1])
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
        local link_task = generator("shlib", {}, { target_node })
        for _, task in ipairs(generator.compiled_tasks) do
            link_task:add_input(task.outputs[1])
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

Bolt = { }

---@param generator Generator
---@param path Node
---@param pattern string
---@return Generator
local function add_source(generator, path, pattern)
    generator.source[1 + #generator.source] = { path, pattern }
    return generator
end

---@param generator Generator
---@param filter fun(Node,Environment):boolean,boolean
---@return Generator
local function set_source_filter(generator, filter)
    generator.source_filter = filter
    return generator
end

---@param generator Generator
---@param path Node
---@return Generator
local function add_public_include(generator, path)
    generator.public_includes[1 + #generator.public_includes] = path
    return generator
end
---@param generator Generator
---@param path Node
---@return Generator
local function add_internal_include(generator, path)
    generator.includes[1 + #generator.includes] = path
    return generator
end

---@param generator Generator
---@param define string
---@param value string|nil
---@return Generator
local function add_public_define(generator, define, value)
    generator.public_defines[1 + #generator.public_defines] = { define, value }
    return generator
end
---@param generator Generator
---@param define string
---@param value string|nil
---@return Generator
local function add_internal_define(generator, define, value)
    generator.defines[1 + #generator.defines] = { define, value }
    return generator
end

---@param generator Generator
---@param dependency Generator
---@return Generator
local function add_public_dependency(generator, dependency)
    generator.public_dependencies[1 + #generator.public_dependencies] = dependency
    return generator
end
---@param generator Generator
---@param dependency Generator
---@return Generator
local function add_internal_dependency(generator, dependency)
    generator.dependencies[1 + #generator.dependencies] = dependency
    return generator
end

---@param env Environment
---@param file Node
---@return boolean,boolean
local function default_filter(env, file)
    return true, false
end

---@param name string
---@param link_type string|nil
---@param languages string[]
---@return Generator
local function module(name, link_type, languages)
    local features = { }
    for _, l in ipairs(languages) do
        features[1 + #features] = l
    end
    features[1 + #features] = link_type
    local g = context(name, features)

    g.objects = { }
    g.source = { }
    g.source_filter = default_filter
    g.includes = { }
    g.public_includes = { }
    g.defines = { }
    g.public_defines = { }
    g.dependencies = { }
    g.public_dependencies = { }

    g.add_source = add_source
    g.set_source_filter = set_source_filter
    g.add_public_include = add_public_include
    g.add_internal_include = add_internal_include
    g.add_public_define = add_public_define
    g.add_internal_define = add_internal_define
    g.add_public_dependency = add_public_dependency
    g.add_internal_dependency = add_internal_dependency
    return g
end

---@param name string
---@param languages string[]
---@return Generator
function Bolt.shared_library(name, languages)
    return module(name, 'shlib', languages)
end

---@param name string
---@param languages string[]
---@return Generator
function Bolt.static_library(name, languages)
    return module(name, 'stlib', languages)
end

---@param name string
---@param languages string[]
---@return Generator
function Bolt.object_library(name, languages)
    return module(name, 'objects', languages)
end

---@param name string
---@param languages string[]
---@return Generator
function Bolt.program(name, languages)
    return module(name, 'program', languages)
end
