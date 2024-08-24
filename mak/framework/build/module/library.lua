---@type Context
local context = ...

---Generates a C/C++ library object. Libraries can take different form based on the value of the `static` and `dynamic`
---flags: when `static` is used, libraries are linked into an archive. When `dynamic` is used, then libraries are linked
---into a shared object. When neither is used, libraries are reated as a collection of object files.
---@param name string name of the library.
---@param dependencies string[] libaries that this library depends on.
function context:library(name, dependencies)
    generator = context(name, 'c,cxx')
    generator.dependencies = dependencies

    local path = string.split(name, '.')
    path = string.join('/', path)
    path = context.path:make_node(path)
end