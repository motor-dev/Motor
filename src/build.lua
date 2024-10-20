local context = ...

local minitl = context:library('motor.minitl', {})
local core = context:library('motor.core', { minitl })
local meta = context:library('motor.meta', { minitl, core })
local filesystem = context:library('motor.filesystem', { minitl, core, meta })