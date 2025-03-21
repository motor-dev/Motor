---@type Context
local context = ...
local env1 = context.env
local env2 = context:derive(env1)
env2.ENV1 = env1
env2.ENV2 = env2
env1.ENV1 = env1
env1.ENV2 = env2
env1.X = 1
env2.X = 4
print(context.env, context.env.ENV1, context.env.ENV2)
print("init", context.env.X, context.env.ENV1.X, context.env.ENV2.X)
local stage1 = context:declare_command('stage1', 'stage1', env1)
local stage2 = context:chain_command(stage1, 'stage2', 'stage2')
context:chain_command(stage2, 'stage3', 'stage3')
