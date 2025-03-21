---@type Context
local context = ...

print(context.env, context.env.ENV1, context.env.ENV2)
print("stage2", context.env.X, context.env.ENV1.X, context.env.ENV2.X)
context.env.ENV1.X = 21
context.env.ENV2.X = 23
context:declare_command('stage3', 'stage3')
