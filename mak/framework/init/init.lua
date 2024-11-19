---@type Context
local context = ...

context:declare_command("configure", "configure", context.env)

context.settings:add_list(
        'compiler',
        'Restrict compiler scanning.\nUse this option several times to scan for additional compilers.'
)      :set_category('Options controlling the configuration')
       :set_long('compiler')

context.settings:add_list(
        'platform',
        'Restrict platform scanning.\nUse this option several times to scan for additional target platforms.'
)      :set_category('Options controlling the configuration')
       :set_long('platform')

context.settings:add_flag(
        'static',
        'Build a completely static executables.\nAll engine components, plugins, samples and kernels will be built into the executable.',
        false
)      :set_category('Options controlling the build')
       :set_long('static')

context.settings:add_flag(
        'dynamic',
        'Build a completely dynamic executables.\nAll engine components, plugins, samples and kernels will be built into shared objects.',
        false
)      :set_category('Options controlling the build')
       :set_long('dynamic')

context.settings:add_flag(
        'nobulk',
        'Disable or enable bulk files.\nBulk files help speed up the build, they are enabled by default.',
        false
)      :set_category('Options controlling the build')
       :set_long('no-bulk')

context.settings:add_flag(
        'werror',
        'Treat compilation warnings as error.',
        false
)      :set_category('Options controlling the build')
       :set_long('werror')

---@param self Context
---@param name string
function context.add_3rd_party_flag(self, name)
    self.settings:add_choice(
            'with_' .. name,
            'Source of the ' .. name .. 'package.\nDefault is `best` (try pkg_config, system, prebuilt, source in that order).\n ',
            { 'best', 'pkg_config', 'system', 'prebuilt', 'source', 'disabled' },

            'best'
    )   :set_category('Options controlling 3rd party libraries')
        :set_long('with-' .. name)
end

context:load_tool('lang/python')
context:load_tool('lang/flex')
context:load_tool('lang/bison')
