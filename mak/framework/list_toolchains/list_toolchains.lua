--- @type Context
local context = ...
local toolchains = context.env.TOOLCHAINS
---@cast toolchains Environment[]
for _, toolchain in ipairs(toolchains) do
    print(toolchain.TOOLCHAIN_ID)
end
