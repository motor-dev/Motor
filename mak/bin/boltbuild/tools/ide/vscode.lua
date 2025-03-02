---@type Context
local context = ...
context:load_tool('internal/module_core')
context:load_tool('ide/cmake')

Bolt.VSCode = {}