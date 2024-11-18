---@type Context
local context = ...

for _, node in ipairs(context:search(context.path, 'motor/3rdparty/**/mak/build.lua')) do
    context:recurse(node:path_from(context.path))
end

local zlib = context:get_generator_by_name('motor.3rdparty.system.zlib')
local minizip = context:get_generator_by_name('motor.3rdparty.system.minizip')

local config = Motor.library('motor.config')
local kernel = Motor.library('motor.kernel')
                    :add_public_dependency(config)
for _, include in ipairs(context:search(context.path, 'motor/kernel/api.cpu', true)) do
    kernel:add_public_include(include)
end

local minitl = Motor.library('motor.minitl')
                    :add_public_dependency(config)
                    :add_public_dependency(kernel)
local core = Motor.library('motor.core')
                  :add_public_dependency(config)
                  :add_public_dependency(kernel)
                  :add_public_dependency(minitl)
local meta = Motor.library('motor.meta')
                  :add_public_dependency(config)
                  :add_public_dependency(kernel)
                  :add_public_dependency(minitl)
                  :add_public_dependency(core)
local filesystem = Motor.library('motor.filesystem')
                        :add_public_dependency(config)
                        :add_public_dependency(kernel)
                        :add_public_dependency(minitl)
                        :add_public_dependency(core)
                        :add_public_dependency(meta)
                        :add_internal_dependency(minizip)
