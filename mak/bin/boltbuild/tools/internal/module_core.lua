---@type Context
local context = ...

context:load_tool('internal/bolt')
context:load_tool('utils/string_ext')

Bolt.ModuleCore = {}
Bolt.ModuleCore.extension_registry = {}


---Register a function that processes an extension
---@param extensions string|string[] an extension, comma-separated extensions or a list of extensions
---@param callback fun(task_gen:Module, source_file:SourceFile):void a function that will be called for every file that matches one of the extensions
function Bolt.ModuleCore.register_extension(extensions, callback)
    if type(extensions) == "string" then
        extensions = extensions:split(',')
    end
    for _, ext in ipairs(extensions) do
        Bolt.ModuleCore.extension_registry[ext] = callback
    end
end
