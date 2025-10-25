---@type Context
local context = ...

context.settings:add_list(
    'compiler',
    'Restrict compiler scanning.\nUse this option several times to scan for additional compilers.'
):set_category('Options controlling the configuration')
    :set_long('compiler')

context.settings:add_list(
    'platform',
    'Restrict platform scanning.\nUse this option several times to scan for additional target platforms.'
):set_category('Options controlling the configuration')
    :set_long('platform')

context.settings:add_flag(
    'static',
    'Build a completely static executables.\nAll engine components, plugins, samples and kernels will be built into the executable.',
    false
):set_category('Options controlling the build')
    :set_long('static')

context.settings:add_flag(
    'dynamic',
    'Build a completely dynamic executables.\nAll engine components, plugins, samples and kernels will be built into shared objects.',
    false
):set_category('Options controlling the build')
    :set_long('dynamic')

context.settings:add_flag(
    'nobulk',
    'Disable or enable bulk files.\nBulk files help speed up the build, they are enabled by default.',
    false
):set_category('Options controlling the build')
    :set_long('no-bulk')

context.settings:add_flag(
    'werror',
    'Treat compilation warnings as error.',
    false
):set_category('Options controlling the build')
    :set_long('werror')

context.settings:add_setting(
    'flavors',
    { 'debug', 'profile', 'final' }
)

MotorOptions = {}
---@param name string
function MotorOptions.add_3rd_party_flag(name)
    context.settings:add_choice(
        'with_' .. name,
        'Source of the ' ..
        name .. 'package.\nDefault is `best` (try pkg_config, system, prebuilt, source in that order).\n ',
        { 'best', 'pkg_config', 'system', 'prebuilt', 'source', 'disabled' },

        'best'
    ):set_category('Options controlling 3rd party libraries')
        :set_long('with-' .. name)
end

context.env.motor_node = context.path.parent.parent.parent
context.settings.name = 'motor'
context.settings.author = 'Motor <motor.devel@gmail.com>'
context.settings.version = '0.1.0'
context.settings.out = context.src_dir:make_node('build/.bolt')
context.settings.tools_dir = {
    context.env.motor_node:make_node("mak/framework/tools"),
}

context:load_tool('internal/sysroot')
context:load_tool('lang/python')
context:load_tool('lang/flex')
context:load_tool('lang/bison')
context:load_tool('tool/wget')


local configure = context:declare_command("configure", "configure")
local setup = context:chain_command(configure, "setup:projects", "setup")
context:chain_command(setup, "clion", "clion")
context:chain_command(setup, "vs2017", "vs2017")
context:chain_command(setup, "vs2019", "vs2019")
context:chain_command(setup, "vs2022", "vs2022")
context:chain_command(setup, "vscode", "vscode")
context:chain_command(setup, "vscode_cmake", "vscode_cmake")
context:chain_command(setup, "qtcreator", "qtcreator")
context:chain_command(setup, "qtcreator_qbs", "qtcreator_qbs")
context:chain_command(setup, "xcode", "xcode")
