---@type Context
local context = ...

context:load_tool('bolt')
context:load_tool('internal/product_process')

---@param generator Generator
---@param path Node
---@param file Node
---@return Generator
local function add_source(generator, path, file)
    generator.source[1 + #generator.source] = { path, file }
    return generator
end

---@param generator Generator
---@param path Node
---@param pattern string
---@return Generator
local function add_source_pattern(generator, path, pattern)
    generator.source_patterns[1 + #generator.source] = { path, pattern }
    return generator
end

---@param generator Generator
---@param filter fun(node:Node,path:Node,env:Environment):boolean,boolean
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

---@param _ Node
---@param _ Node
---@param _ Environment
---@return boolean,boolean
local function default_filter(_, _, _)
    return true, false
end

---@param name string
---@param link_type string|nil
---@param languages string[]
---@param group string|nil
---@return Generator
function Bolt.module(name, link_type, languages, group)
    local features = { }
    for _, l in ipairs(languages) do
        features[1 + #features] = l
    end
    if link_type then
        features[1 + #features] = link_type
    end
    local g = context:declare_generator(name, features, context.env, group)

    g.objects = { }
    g.source = { }
    g.source_patterns = { }
    g.source_filter = default_filter
    g.includes = { }
    g.public_includes = { }
    g.defines = { }
    g.public_defines = { }
    g.dependencies = { }
    g.public_dependencies = { }
    g.public_flags = { }
    g.libs = { }
    g.libpaths = { }
    g.linkflags = { }

    g.add_source = add_source
    g.add_source_pattern = add_source_pattern
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
---@param group string|nil
---@return Generator
function Bolt.shared_library(name, languages, group)
    return Bolt.module(name, 'shlib', languages, group)
end

---@param name string
---@param languages string[]
---@param group string|nil
---@return Generator
function Bolt.static_library(name, languages, group)
    return Bolt.module(name, 'stlib', languages, group)
end

---@param name string
---@param languages string[]
---@param group string|nil
---@return Generator
function Bolt.object_library(name, languages, group)
    return Bolt.module(name, 'objects', languages, group)
end

---@param name string
---@param languages string[]
---@param group string|nil
---@return Generator
function Bolt.program(name, languages, group)
    return Bolt.module(name, 'program', languages, group)
end

function Bolt.pkg_config(name, var)
    if context.env['check_' .. var] then
        local cflags = context.env['check_' .. var .. '_cflags']
        local libs = context.env['check_' .. var .. '_libs']
        local ldflags = context.env['check_' .. var .. '_ldflags']
        local generator = Bolt.module(name, nil, { 'c', 'cxx' })
        generator.public_flags = { { 'CFLAGS', cflags },
                                   { 'CXXFLAGS', cflags } }
        generator.linkflags = ldflags
        generator.libs = libs
    end
end
