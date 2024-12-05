---@type Context
local context = ...

Bolt.Module = {}

Bolt.Module.extension_registry = {}


context:load_tool('utils/string_ext')

---Register a function that processes an extension
---@param extensions string|string[] an extension, comma-separated extensions or a list of extensions
---@param callback fun(task_gen:Module, source_file:SourceFile):void a function that will be called for every file that matches one of the extensions
function Bolt.Module.register_extension(extensions, callback)
    if type(extensions) == "string" then
        extensions = extensions:split(',')
    end
    for _, ext in ipairs(extensions) do
        Bolt.Module.extension_registry[ext] = callback
    end
end
