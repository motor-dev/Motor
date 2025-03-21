---@type Context
local context = ...
print(context.env, context.env.ENV1, context.env.ENV2)
print("stage1", context.env.X, context.env.ENV1.X, context.env.ENV2.X)
context.env.ENV1.X = 11
context.env.ENV2.X = 13
local stage2 = context:declare_command('stage2', 'stage2')
context:chain_command(stage2, 'stage3', 'stage3')
