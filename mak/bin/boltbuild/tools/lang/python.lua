---@type Context
local context = ...
context:load_tool('bolt')

Bolt.Python = {}

function Bolt.Python.find_python()
    if not context.env.PYTHON then
        context:try('Looking for python', function()
            local python = context:find_program('python3')
            if not python then
                python = context:find_program('python')
            end
            context.env.PYTHON = python
            if python then
                return python
            else
                error('Python not found')
            end
        end)
    end
end