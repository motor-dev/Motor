---@type Context
local context = ...
if context.fun == "init" then
    context:declare_command('test', 'test')
else
    context:load_tool("tool/copy")
    context:load_tool("tool/patch")

    generator = context:declare_generator("patch", {})
    Bolt.Patch.patch(generator, context.path:make_node("patches/vinyl.patch"), context.path:make_node('src'), context.bld_dir:make_node('int'), 0)
    Bolt.Patch.patch(generator, context.path:make_node("patches/all.patch"), context.bld_dir:make_node('int'), context.bld_dir:make_node('dst'), 0)
    Bolt.Patch.patch(generator, {context.path:make_node("patches/vinyl.patch"), context.path:make_node('patches/all.patch')}, context.path:make_node('src'), context.bld_dir:make_node('dst2'), 0)
end
