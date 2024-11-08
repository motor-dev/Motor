local context = ...

local config = Motor.library('motor.config', {})
local minitl = Motor.library('motor.minitl', {})
local core = Motor.library('motor.core', { minitl })
local meta = Motor.library('motor.meta', { minitl, core })
local filesystem = Motor.library('motor.filesystem', { minitl, core, meta })