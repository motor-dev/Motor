---@type Context
local context = ...

---@param source_file SourceFile
---@param env Environment
---@return boolean,boolean
local function filter_source(source_file, env)
    local add = true
    local matched = false
    local found = true

    local directory, node = source_file.base_path, source_file.full_path

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

local function module(name, namespace, path, lib_types)
    local name_components = string.split(name, '.')
    path = path or string.join('/', name_components)
    path = context.path:make_node(path)
    local module_name = name_components[#name_components]

    local lib_type = lib_types[1]
    if context.settings.static then
        lib_type = lib_types[2]
    elseif context.settings.dynamic then
        lib_type = lib_types[3]
    end

    local meta_generator = metagen(name, path)

    if context.settings.nobulk then
        group = group .. '.nobulk'
    end

    local generator = Bolt.Module.module(name, {
        features = { lib_type, 'motor_module' },
        source_patterns = {
            { path = path, pattern = 'src/**/*' }
        },
        source_filter = filter_source,
        internal_defines = {
            { 'building_' .. module_name, '1' },
            { 'MOTOR_PROJECTID', namespace }
        },
        public_defines = {
            { 'motor_dll_' .. module_name, '1' }
        },
        public_includes = {
            context.bld_dir:make_node(meta_generator.group):make_node(meta_generator.name):make_node('api')
        },
        internal_includes = {
            context.bld_dir:make_node(meta_generator.group):make_node(meta_generator.name):make_node('include')
        }
    })
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
---@param namespace string root namespace of meta objects.
---@param path string? qualified path of the library. Defaults to name.
---@return Module a new library module
function Motor.library(name, namespace, path)
    return module(name, namespace,path, { 'objects', 'objects', 'shlib' })
end

---Generates a C/C++ shared library object.
---@param name string name of the library.
---@param namespace string root namespace of meta objects.
---@param path string? qualified path of the library. Defaults to name.
function Motor.shared_library(name, namespace, path)
    return module(name, namespace, path, { 'shlib', 'objects', 'shlib' })
end

local function propagate_building_macro(module, current, seen)
    if seen[current] then
        return
    end
    seen[current] = true
    if current:has_all_features({"objects", "motor_module"}) then
        local name_components = string.split(current.name, '.')
        local module_name = name_components[#name_components]
        module:add_internal_define('building_' .. module_name, '1')
        for _, dep in ipairs(current.internal_dependencies) do
            propagate_building_macro(module, dep, seen)
        end
        for _, dep in ipairs(current.public_dependencies) do
            propagate_building_macro(module, dep, seen)
        end
    end
end

context:feature("motor_module", "motor_propagate_building_macro", function (module)
    for _, dep in ipairs(module.internal_dependencies) do
        propagate_building_macro(module, dep, {})
    end
    for _, dep in ipairs(module.public_dependencies) do
        propagate_building_macro(module, dep, {})
    end
end):set_run_before({'process_flags'})
