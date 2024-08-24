---@meta

local function use(var)return var end

---@class Generator
---@field name string The name of the generator.
---@field stage string The build stage this generator belongs to. By default, all stages are built.
---                    Stages can be shared between different build commands.
Generator = {}
