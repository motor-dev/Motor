---@type Context
local context = ...

Bolt.Python.find_python()

context.env.METAGEN = context.path:make_node('../../bin/metagen.py')
context.env.METAGEN_TMP = context.bld_dir
context.env.METAGEN_MACROS = context.path:make_node('../../tools/macros_def.json')