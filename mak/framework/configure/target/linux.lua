---@type Context
local context = ...

for _, compiler in ipairs(--[[---@type Compiler[] ]] context.compilers) do
    if compiler.target:find('%-linux%-gnu') then
        context:create_toolchain(compiler, context.Platform:new {
            name = "linux",
            setup = function(compiler)
            end
        })
    end
end