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

local function empty(_module)
end

-- build stages for modules

-- stage 1: process dependencies and propagate flags
context
    :feature('module', 'start_dependencies', empty)
context
    :feature('module', 'end_dependencies', empty)
    :set_run_after({ 'start_dependencies' })

-- stage 2: process source files. source files get consumed and turned into object files.
context
    :feature('module', 'start_source', empty)
    :set_run_after({ "end_dependencies" })
context
    :feature('module', 'end_source', empty)
    :set_run_after({ "start_source" })

-- stage 3: link the object files into the final target
context
    :feature('module', 'start_link', empty)
    :set_run_after({ "end_source" })
context
    :feature('module', 'end_link', empty)
    :set_run_after({ "start_link" })

-- stage 4: post-link steps
context
    :feature('module', 'start_post_link', empty)
    :set_run_after({ "end_link" })
context
    :feature('module', 'end_post_link', empty)
    :set_run_after({ "start_post_link" })

-- stage 5: install/copy
context
    :feature('module', 'start_deploy', empty)
    :set_run_after({ "end_post_link" })
context
    :feature('module', 'end_deploy', empty)
    :set_run_after({ "start_deploy" })
