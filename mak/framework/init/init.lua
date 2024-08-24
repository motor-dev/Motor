---@type Context
local context = ...

context:declare_command("configure", "configure", context.env)

context.settings:add_list(
        'compiler',
        'Restrict compiler scanning.\nUse this option several times to scan for additional compilers.',
        'Options controlling the configuration',
        'compiler'
)

context.settings:add_list(
        'platform',
        'Restrict platform scanning.\nUse this option several times to scan for additional target platforms.',
        'Options controlling the configuration',
        'platform'
)

context.settings:add_flag(
        'static',
        'Build a completely static executables.\nAll engine components, plugins, samples and kernels will be built into the executable.',
        'Options controlling the build',
        'static',
        nil,
        false
)

context.settings:add_flag(
        'dynamic',
        'Build a completely dynamic executables.\nAll engine components, plugins, samples and kernels will be built into shared objects.',
        'Options controlling the build',
        'dynamic',
        nil,
        false
)

context.settings:add_flag(
        'bulk',
        'Disable or enable bulk files.\nBulk files help speed up the build, they are enabled by default.',
        'Options controlling the build',
        'bulk',
        nil,
        true
)

context.settings:add_flag(
        'werror',
        'Treat compilation warnings as error.',
        'Options controlling the build',
        'werror',
        nil,
        false
)

---@param self Context
---@param name string
function context.add_3rd_party_flag(self, name)
    self.settings:add_choice(
            'with_' .. name,
            'Source of the ' .. name .. 'package.\nDefault is `best` (try pkg_config, system, prebuilt, source in that order).\n ',
            { 'best', 'pkg_config', 'system', 'prebuilt', 'source', 'disabled' },
            'Options controlling 3rd party libraries',
            'with-' .. name,
            nil,
            'best'
    )
end
