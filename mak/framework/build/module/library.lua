---@type Context
local context = ...

---@param node Node
---@param directory Node
---@param env Environment
---@return boolean,boolean
local function filter_source(node, directory, env)
    local add = true
    local matched = false
    local found = true

    local platform_set = {}
    local arch_set = {}
    for _, platform in ipairs(env.MOTOR_PLATFORMS) do
        platform_set[platform] = true
    end
    for _, arch in ipairs(env.MOTOR_ARCHITECTURES) do
        arch_set[arch] = true
    end

    local platforms = node:name():match("-p{(.*)}")
    if platforms then
        platforms = platforms:split('+')
        matched = true
        found = false
        for _, p in ipairs(platforms) do
            if platform_set[p] then
                found = true
                break
            end
        end
        add = add and found
    end
    local archs = node:name():match("-a{(.*)}")
    if archs then
        archs = archs:split('+')
        matched = true
        found = false
        for _, a in ipairs(archs) do
            if arch_set[a] then
                found = true
                break
            end
        end
        add = add and found
    end

    while tostring(node) ~= tostring(directory) do
        node = node.parent
        platforms = node:name():match("^platform{(.*)}$")
        if platforms then
            platforms = platforms:split('+')
            matched = true
            found = false
            for _, p in ipairs(platforms) do
                if platform_set[p] then
                    found = true
                    break
                end
            end
            add = add and found
        end

        archs = node:name():match("^arch{(.*)}$")
        if archs then
            archs = archs:split('+')
            matched = true
            found = false
            for _, a in ipairs(archs) do
                if arch_set[a] then
                    found = true
                    break
                end
            end
            add = add and found
        end
    end
    return add, matched
end

local function metagen(name, path)
    local api = string.split(name, '.')
    api = api[#api]
    name = name .. '.metagen'
    local generator = context:declare_generator(name, { 'metagen' }, context.env, "metagen")
    generator.source = { path:make_node('api'), path:make_node('include') }
    generator.out_source = {}
    generator.api = api:upper()
    return generator
end

local function module(name, path, lib_types)
    path = path or string.join('/', string.split(name, '.'))
    path = context.path:make_node(path)
    local module_name = path:name()

    local group = context.fs_name
    local lib_type = lib_types[1]
    if context.settings.static then
        lib_type = lib_types[2]
        group = group .. '.static'
    elseif context.settings.dynamic then
        group = group .. '.dynamic'
        lib_type = lib_types[3]
    end

    local meta_generator = metagen(name, path)

    if context.settings.nobulk then
        group = group .. '.nobulk'
    end

    local generator = Bolt.module(name, lib_type, { 'c', 'cxx' }, group)
                          :add_source_pattern(path, 'src/**/*')
                          :set_source_filter(filter_source)
                          :add_internal_define('building_' .. module_name, '1')
                          :add_public_define('motor_dll_' .. module_name, '1')
                          :add_public_include(context.bld_dir:make_node(meta_generator.group):make_node(meta_generator.name):make_node('api'))
                          :add_internal_include(context.bld_dir:make_node(meta_generator.group):make_node(meta_generator.name):make_node('include'))
    generator.bulk = context.settings.bulk
    for _, include in ipairs(context:search(path, 'include', true)) do
        generator = generator:add_internal_include(include)
    end
    for _, include in ipairs(context:search(path, 'api', true)) do
        generator = generator:add_public_include(include)
    end

    return generator
end

---Generates a C/C++ library object. Libraries can take different form based on the value of the `static` and `dynamic`
---flags: when `static` is used, libraries are linked into an archive. When `dynamic` is used, then libraries are linked
---into a shared object. When neither is used, libraries are a collection of object files that are directly pulled into
---the link phase of modules depending on them.
---@param name string name of the library.
---@param path string|nil qualified path of the library. Defaults to name.
function Motor.library(name, path)
    return module(name, path, { 'objects', 'objects', 'shlib' })
end

---Generates a C/C++ shared library object.
---@param name string name of the library.
---@param path string|nil qualified path of the library. Defaults to name.
function Motor.shared_library(name, path)
    return module(name, path, { 'shlib', 'objects', 'shlib' })
end
