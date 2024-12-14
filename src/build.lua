---@type Context
local context = ...

for _, node in ipairs(context:search(context.path, 'motor/3rdparty/**/mak/build.lua')) do
    context:recurse(node:path_from(context.path))
end

local zlib = context:get_generator_by_name('motor.3rdparty.system.zlib')
local minizip = context:get_generator_by_name('motor.3rdparty.system.minizip')

local config = Motor.module('motor.config')
local kernel = Motor.module('motor.kernel')
                    :add_public_dependency(config)
for _, include in ipairs(context:search(context.path, 'motor/kernel/api.cpu', true)) do
    kernel:add_public_include(include)
end

local minitl = Motor.module('motor.minitl')
    :add_public_dependencies({config, kernel})
local core = Motor.module('motor.core')
    :add_public_dependencies({config, kernel, minitl})
local meta = Motor.module('motor.meta')
    :add_public_dependencies({config, kernel, minitl, core})
    :add_internal_dependency(zlib)
local filesystem = Motor.module('motor.filesystem')
    :add_public_dependencies({config, kernel, minitl, core, meta})
    :add_internal_dependency(minizip)
local introspect = Motor.module('motor.introspect')
    :add_public_dependencies({config, kernel, minitl, core, meta, filesystem})
local reflection = Motor.module('motor.reflection')
    :add_public_dependencies({config, kernel, minitl, core, meta, filesystem, introspect})
local settings = Motor.module('motor.settings')
    :add_public_dependencies({config, kernel, minitl, core, meta, filesystem, introspect, reflection})
local resource = Motor.module('motor.resource')
    :add_public_dependencies({config, kernel, minitl, core, meta, filesystem})
local scheduler = Motor.module('motor.scheduler')
    :add_public_dependencies({config, kernel, minitl, core, meta, filesystem, resource, settings})
local plugin = Motor.module('motor.plugin')
    :add_public_dependencies({config, kernel, minitl, core, meta, filesystem, resource, settings, scheduler})
local world = Motor.module('motor.world')
    :add_public_dependencies({config, kernel, minitl, core, meta, filesystem, resource, settings, scheduler, plugin})

local motor = Motor.package('motor', 'motor', 'motor/motor')
    :add_public_dependencies({
        config, kernel, minitl, core, meta, filesystem, introspect, reflection, resource, settings, scheduler, plugin, world
    })
