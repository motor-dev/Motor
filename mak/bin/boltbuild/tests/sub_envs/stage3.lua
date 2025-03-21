---@type Context
local context = ...

print(context.env, context.env.ENV1, context.env.ENV2)
print("stage3", context.env.X, context.env.ENV1.X, context.env.ENV2.X)
