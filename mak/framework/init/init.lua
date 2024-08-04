local context = ...
configure = context:declare_command("configure", "configure", context.env)

context.settings:add_list(
        'compiler',
        'Options controlling the configuration',
        'compiler',
        nil,
        'Restrict compiler scanning.\nUse this option several times to scan for additional compilers.',
        false
)

context.settings:add_flag(
        'static',
        'Options controlling the build',
        'static',
        nil,
        'Build a completely static executables.\nAll engine components, plugins, samples and kernels will be built into the executable.',
        false
)
context.settings:add_flag(
        'dynamic',
        'Options controlling the build',
        'dynamic',
        nil,
        'Build a completely dynamic executables.\nAll engine components, plugins, samples and kernels will be built into shared objects.',
        false
)
context.settings:add_flag(
        'bulk',
        'Options controlling the build',
        'bulk',
        nil,
        'Disable or enable bulk files.\nBulk files help speed up the build, they are enabled by default.',
        true
)
context.settings:add_flag(
        'werror',
        'Options controlling the build',
        'werror',
        nil,
        'Treat compilation warnings as error.',
        false
)

function context.add_3rd_party_flag(self, name)
    self.settings:add_choice(
            'with_' .. name,
            'Options controlling 3rd party libraries',
            'with-' .. name,
            nil,
            'Source of the ' .. name .. 'package.\nDefault is `best` (try pkgconfig, system, prebuilt, source in that order).\n ',
            { 'best', 'pkgconfig', 'system', 'prebuilt', 'source', 'disabled' },
            'best')
end
