---@type Context
local context = ...

BoltPython.find_python()

context.env.METAGEN = context.path:make_node('../../bin/metagen.py')
context.env.METAGEN_TMP = context.bld_dir
context.env.METAGEN_MACROS = context.path:make_node('../../tools/macros_def.json')
context.env.METAGEN_NODES = context:search(context.path:make_node('../../lib/pyxx'), '**/*')
context.env:append('METAGEN_NODES', context:search(context.path:make_node('../../lib/glrp'), '**/*'))
context.env:append('METAGEN_NODES', context.env.METAGEN)