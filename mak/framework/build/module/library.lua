---@type Context
local context = ...

---Generates a C/C++ library object. Libraries can take different form based on the value of the `static` and `dynamic`
---flags: when `static` is used, libraries are linked into an archive. When `dynamic` is used, then libraries are linked
---into a shared object. When neither is used, libraries are reated as a collection of object files.
---@param name string name of the library.
function Motor.library(name)
    local path = string.split(name, '.')
    path = string.join('/', path)
    path = context.path:make_node(path)

    local generator = Bolt.shared_library(name, { 'c', 'cxx' })
                          :set_path(path)
                          :add_source('src/**/*')
    for _, include in ipairs(context:search(path, 'include', true)) do
        generator = generator:add_internal_include(include)
    end
    for _, include in ipairs(context:search(path, 'api', true)) do
        generator = generator:add_public_include(include)
    end

    return generator
end
