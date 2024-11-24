---@type Context
local context = ...

context:load_tool('internal/module_core')
context:load_tool('internal/module_process')

---@class Module : Generator
---@field objects Node[]
local Module = {}

---@class CppProperties
---@field group string|nil
---@field public_includes Node[]|nil
---@field internal_includes Node[]|nil
---@field public_defines string[]|nil
---@field internal_defines string[]|nil
---@field public_dependencies string[]|nil
---@field internal_dependencies string[]|nil
---@field source string[]|nil
---@field source_patterns string[]|nil
---@field source_filter nil|fun(node:Node, directory:Node, env:Environment):boolean,boolean
---@field bulk boolean|nil
---@field public_flags string[]|nil

---@param path Node
---@param file Node
---@return Module
function Module:add_source(path, file)
    table.insert(self.source, { path, file })
    return self
end

---@param path Node
---@param pattern string
---@return Module
function Module:add_source_pattern(path, pattern)
    table.insert(self.source_patterns, { path, pattern })
    return self
end

---@param filter fun(node:Node,path:Node,env:Environment):boolean,boolean
---@return Module
function Module:set_source_filter(filter)
    self.source_filter = filter
    return self
end

---@param path Node
---@return Module
function Module:add_public_include(path)
    table.insert(self.public_includes, path)
    return self
end
---@param path Node
---@return Module
function Module:add_internal_include(path)
    table.insert(self.internal_includes, path)
    return self
end

---@param define string
---@param value string|nil
---@return Module
function Module:add_public_define(define, value)
    table.insert(self.public_defines, { define, value })
    return self
end

---@param define string
---@param value string|nil
---@return Module
function Module:add_internal_define(define, value)
    table.insert(self.internal_defines, { define, value })
    return self
end

---@param dependency Generator
---@return Module
function Module:add_public_dependency(dependency)
    table.insert(self.public_dependencies, dependency)
    return self
end

---@param dependency Generator
---@return Module
function Module:add_internal_dependency(dependency)
    table.insert(self.internal_dependencies, dependency)
    return self
end

---@param _ Node
---@param _ Node
---@param _ Environment
---@return boolean,boolean
function Module.default_filter(_, _, _)
    return true, false
end

---@param name string
---@param link_type string|nil
---@param languages string[]
---@param group string|nil
---@return Module
function BoltModule.module(name, link_type, languages, group)
    local features = { }
    for _, l in ipairs(languages) do
        table.insert(features, l)
    end
    if link_type then
        table.insert(features, link_type)
    end
    local g = context:declare_generator(name, features, context.env, group)

    g.objects = { }
    g.source = { }
    g.source_patterns = { }
    g.source_filter = default_filter
    g.internal_includes = { }
    g.public_includes = { }
    g.internal_defines = { }
    g.public_defines = { }
    g.internal_dependencies = { }
    g.public_dependencies = { }
    g.public_flags = { }
    g.libs = { }
    g.libpaths = { }
    g.linkflags = { }

    g.add_source = Module.add_source
    g.add_source_pattern = Module.add_source_pattern
    g.set_source_filter = Module.set_source_filter
    g.add_public_include = Module.add_public_include
    g.add_internal_include = Module.add_internal_include
    g.add_public_define = Module.add_public_define
    g.add_internal_define = Module.add_internal_define
    g.add_public_dependency = Module.add_public_dependency
    g.add_internal_dependency = Module.add_internal_dependency

    return g
end

---@param name string
---@param languages string[]
---@param group string|nil
---@return Module
function BoltModule.shared_library(name, languages, group)
    return BoltModule.module(name, 'shlib', languages, group)
end

---@param name string
---@param languages string[]
---@param group string|nil
---@return Module
function BoltModule.static_library(name, languages, group)
    return BoltModule.module(name, 'stlib', languages, group)
end

---@param name string
---@param languages string[]
---@param group string|nil
---@return Module
function BoltModule.object_library(name, languages, group)
    return BoltModule.module(name, 'objects', languages, group)
end

---@param name string
---@param languages string[]
---@param group string|nil
---@return Module
function BoltModule.program(name, languages, group)
    return BoltModule.module(name, 'program', languages, group)
end

function BoltModule.pkg_config(name, var)
    if context.env['check_' .. var] then
        local cflags = context.env['check_' .. var .. '_cflags']
        local libs = context.env['check_' .. var .. '_libs']
        local ldflags = context.env['check_' .. var .. '_ldflags']
        local generator = BoltModule.module(name, nil, { 'c', 'cxx' })
        generator.public_flags = { { 'CFLAGS', cflags },
                                   { 'CXXFLAGS', cflags } }
        generator.linkflags = ldflags
        generator.libs = libs
    end
end
