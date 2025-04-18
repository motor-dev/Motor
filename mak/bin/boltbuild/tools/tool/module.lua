---@type Context
local context = ...

context:load_tool('internal/module_core')
context:load_tool('internal/module_process')

Bolt.Module = {}

---@class (exact) SourcePattern
---@field path Node
---@field pattern string
local _

---@class (exact) SourceFile
---@field base_path Node
---@field full_path Node
local _

---@class (exact) ModuleProperties
---@field features string[]?
---@field group string?
---@field public_includes Node[]?
---@field internal_includes Node[]?
---@field public_defines [string,string][]?
---@field internal_defines [string,string][]?
---@field public_dependencies Module[]?
---@field internal_dependencies Module[]?
---@field public_flags table<string,string[]>?
---@field internal_flags table<string,string[]>?
---@field flag_groups string[]?
---@field source SourceFile[]?
---@field source_patterns SourcePattern[]?
---@field source_filter (fun(source_file:SourceFile,env:Environment):[boolean,boolean]) ?
local _

---@class Module : Generator
---@field target string
---@field objects Node[]
---@field source SourceFile[]
---@field source_patterns SourcePattern[]
---@field source_filter fun(source_file:SourceFile,env:Environment):[boolean,boolean]
---@field internal_includes Node[]
---@field public_includes Node[]
---@field internal_defines [string,string][]
---@field public_defines [string,string][]
---@field internal_dependencies Module[]
---@field public_dependencies Module[]
---@field internal_flags table<string,string[]>
---@field public_flags table<string,string[]>
---@field flag_groups string[]
---@field link_task Task?
---@field compiled_tasks Task[]
---@field dep_link_tasks Task[]
local Module = {}

---@param path Node
---@param file Node
---@return Module
function Module:add_source(path, file)
    table.insert(self.source, { base_path = path, full_path = file })
    return self
end

---@param path Node
---@param pattern string
---@return Module
function Module:add_source_pattern(path, pattern)
    table.insert(self.source_patterns, { path = path, pattern = pattern })
    return self
end

---@param filter fun(source_file:SourceFile,env:Environment):boolean,boolean
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

---@param dependencies Generator[]
---@return Module
function Module:add_public_dependencies(dependencies)
    for _, dependency in ipairs(dependencies) do
        table.insert(self.public_dependencies, dependency)
    end
    return self
end

---@param dependency Generator
---@return Module
function Module:add_internal_dependency(dependency)
    table.insert(self.internal_dependencies, dependency)
    return self
end

---@param dependencies Generator[]
---@return Module
function Module:add_internal_dependencies(dependencies)
    for _, dependency in ipairs(dependencies) do
        table.insert(self.internal_dependencies, dependency)
    end
    return self
end

---@param source_file SourceFile
---@param category string?
---@return Node,Node
function Module:make_build_node(source_file, category)
    category = category or 'obj'
    local directory = self.bld_dir:make_node(category)
    local target_node = directory:make_node(source_file.full_path:path_from(source_file.base_path))
    target_node = target_node:change_ext("o")
    return target_node, directory
end

---@param pattern string
---@param env? Environment
---@return string
function Module:make_build_target(pattern, env)
    env = env or self.env
    ---@type string
    pattern = env[pattern]
    if pattern == nil then
        return self.target
    else
        return string.format(pattern, self.target)
    end
end

local function default_filter(_, _)
    return true, false
end

---@param name string
---@param properties ModuleProperties
---@return Module
function Bolt.Module.module(name, properties)
    local features = properties.features or {} ---@type string[]
    table.insert(features, 1, 'module')
    local g = context:declare_generator(name, features, context.env, properties.group)
    ---@cast g Module

    local name_parts = name:split('/')

    g.objects = {}
    g.compiled_tasks = {}
    g.target = name_parts[#name_parts]:gsub("%?<>:%*|%\"", "-")
    g.source = properties.source or {}
    g.source_patterns = properties.source_patterns or {}
    g.source_filter = properties.source_filter or default_filter
    g.internal_includes = properties.internal_includes or {}
    g.public_includes = properties.public_includes or {}
    g.internal_defines = properties.internal_defines or {}
    g.public_defines = properties.public_defines or {}
    g.internal_dependencies = properties.internal_dependencies or {}
    g.public_dependencies = properties.public_dependencies or {}
    g.internal_flags = properties.internal_flags or {}
    g.public_flags = properties.public_flags or {}
    g.flag_groups = properties.flag_groups or {}
    g.link_task = nil
    g.dep_link_tasks = {}

    g.add_source = Module.add_source
    g.add_source_pattern = Module.add_source_pattern
    g.set_source_filter = Module.set_source_filter
    g.add_public_include = Module.add_public_include
    g.add_internal_include = Module.add_internal_include
    g.add_public_define = Module.add_public_define
    g.add_internal_define = Module.add_internal_define
    g.add_public_dependency = Module.add_public_dependency
    g.add_internal_dependency = Module.add_internal_dependency
    g.add_public_dependencies = Module.add_public_dependencies
    g.add_internal_dependencies = Module.add_internal_dependencies
    g.make_build_node = Module.make_build_node
    g.make_build_target = Module.make_build_target

    return g
end

---@param name string
---@param properties ModuleProperties
---@return Module
function Bolt.Module.shared_library(name, properties)
    if properties.features then
        table.insert(properties.features, 'shlib')
    else
        properties.features = { 'shlib' }
    end
    return Bolt.Module.module(name, properties)
end

---@param name string
---@param properties ModuleProperties
---@return Module
function Bolt.Module.static_library(name, properties)
    if properties.features then
        table.insert(properties.features, 'stlib')
    else
        properties.features = { 'stlib' }
    end
    return Bolt.Module.module(name, properties)
end

---@param name string
---@param properties ModuleProperties
---@return Module
function Bolt.Module.object_library(name, properties)
    if properties.features then
        table.insert(properties.features, 'objects')
    else
        properties.features = { 'objects' }
    end
    return Bolt.Module.module(name, properties)
end

---@param name string
---@param properties ModuleProperties
---@return Module
function Bolt.Module.program(name, properties)
    if properties.features then
        table.insert(properties.features, 'program')
    else
        properties.features = { 'program' }
    end
    return Bolt.Module.module(name, properties)
end

function Bolt.Module.pkg_config(name, var)
    if context.env['check_' .. var] then
        local cflags = context.env['check_' .. var .. '_cflags'] ---@type string[]
        local libs = context.env['check_' .. var .. '_libs'] ---@type string[]
        local ldflags = context.env['check_' .. var .. '_ldflags'] ---@type string[]
        ---@type ModuleProperties
        local properties = { public_flags = { CFLAGS = cflags, CXXFLAGS = cflags, LINKFLAGS = ldflags, LIBS = libs } }
        return Bolt.Module.module(name, properties)
    end
end
