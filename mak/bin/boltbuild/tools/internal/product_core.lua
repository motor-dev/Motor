---@type Context
local context = ...

context:load_tool('utils/string_ext')
context._extensions = {}

---Register a function that processes an extension
---@param extensions string|string[] an extension, comma-separated extensions or a list of extensions
---@param callback function(task_gen:Generator, node:Node, path:Node) a function that will be called for every file that matches one of the extensions
function context:extension(extensions, callback)
    if type(extensions) == "string" then
        extensions = extensions:split(',')
    end
    for _, ext in ipairs(extensions) do
        context._extensions[ext] = callback
    end
end
