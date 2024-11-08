---@type Context
local context = ...

Bolt = { }

---@param generator Generator
---@param pattern string
---@return Generator
local function add_source(generator, pattern)
    generator.source[1 + #generator.source] = pattern
    return generator
end


---@param generator Generator
---@param path Node
---@return Generator
local function set_path(generator, path)
    generator.path = path
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
---@param value string?
---@return Generator
local function add_public_define(generator, define, value)
    generator.public_defines[1 + #generator.public_defines] = { define, value }
    return generator
end
---@param generator Generator
---@param define string
---@param value string?
---@return Generator
local function add_internal_define(generator, define, value)
    generator.public_defines[1 + #generator.public_defines] = { define, value }
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

---@param _env Environment
---@param _file Node
local function default_filter(_env, _file)
    return true
end

---@param name string
---@param link_type string?
---@param languages string[]
---@return Generator
local function module(name, link_type, languages)
    local features = { }
    for _, l in ipairs(languages) do
        features[1 + #features] = l
    end
    features[1 + #features] = link_type
    local g = context(name, features)

    g.path = context.path
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
    g.set_path = set_path
    g.add_public_include = add_public_include
    g.add_internal_include = add_internal_include
    g.add_public_define = add_public_define
    g.add_internal_define = add_internal_define
    g.add_public_include = add_public_dependency
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
