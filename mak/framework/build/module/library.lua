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

local function metagen(name)
    local path = string.split(name, '.')
    path = string.join('/', path)
    path = context.path:make_node(path)

    name = name .. '.metagen'
    local generator = context:declare_generator(name, { 'metagen' }, context.env, "metagen")
    generator.source = { path:make_node('api'), path:make_node('include') }
    generator.out_source = {}
    return generator
end

---Generates a C/C++ library object. Libraries can take different form based on the value of the `static` and `dynamic`
---flags: when `static` is used, libraries are linked into an archive. When `dynamic` is used, then libraries are linked
---into a shared object. When neither is used, libraries are reated as a collection of object files.
---@param name string name of the library.
function Motor.library(name)
    local path = string.split(name, '.')
    path = string.join('/', path)
    path = context.path:make_node(path)
    local module_name = path:name()

    local meta_generator = metagen(name)

    local generator = Bolt.shared_library(name, { 'c', 'cxx' })
                          :add_source_pattern(path, 'src/**/*')
                          :set_source_filter(filter_source)
                          :add_internal_define('building_' .. module_name, '1')
                          :add_public_define('motor_dll_' .. module_name, '1')
                          :add_public_include(context.bld_dir:make_node(meta_generator.group):make_node(meta_generator.name):make_node('api'))
                          :add_internal_include(context.bld_dir:make_node(meta_generator.group):make_node(meta_generator.name):make_node('include'))
    for _, include in ipairs(context:search(path, 'include', true)) do
        generator = generator:add_internal_include(include)
    end
    for _, include in ipairs(context:search(path, 'api', true)) do
        generator = generator:add_public_include(include)
    end

    return generator
end
