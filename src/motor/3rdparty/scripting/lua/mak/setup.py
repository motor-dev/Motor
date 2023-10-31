import build_framework
import waflib.Errors
import waflib.Options

LUA_SOURCES = 'https://www.lua.org/ftp/lua-5.3.5.tar.gz'
LUA_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/' \
               'lua-5.3.5-%(platform)s-%(arch)s-%(abi)s.tgz'


def setup_pkgconfig(setup_context: build_framework.SetupContext) -> bool:
    for v in '-5.4', '5.4', '-5.3', '5.3', '-5.2', '5.2', '-5.1', '5.1':
        try:
            build_framework.pkg_config(setup_context, 'lua%s' % v, var='lua')
        except waflib.Errors.WafError:
            pass
        else:
            setup_context.env.LUA_BINARY = True
            setup_context.end_msg('version %s from pkg-config' % v)
            return True
    else:
        return False


def setup_system(setup_context: build_framework.SetupContext) -> bool:
    if 'windows' not in setup_context.env.VALID_PLATFORMS:
        for v in '-5.4', '5.4', '-5.3', '5.3', '-5.2', '5.2', '-5.1', '5.1':
            version = '%s%s' % (v[-3], v[-1])
            if build_framework.check_lib(
                    setup_context,
                    ['lua%s' % v],
                    var='lua',
                    includepath=['=/usr/include/lua%s' % version,
                                 '=/usr/local/include/lua%s' % version],
                    includes_externc=['lua.h'],
                    functions=['lua_newstate']
            ):
                setup_context.env.LUA_BINARY = True
                setup_context.end_msg('version %s from system' % v)
                return True
    return False


def setup_prebuilt(setup_context: build_framework.SetupContext) -> bool:
    try:
        node = build_framework.pkg_unpack(setup_context, 'lua_bin_%(platform)s-%(arch)s-%(abi)s', LUA_BINARIES)
        if not build_framework.check_package(setup_context, ['motor.3rdparty.scripting.lua'], node, var='lua'):
            raise waflib.Errors.WafError('no prebuilt binaries')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.LUA_BINARY = node.path_from(setup_context.package_node)
        setup_context.end_msg('from prebuilt')
        return True


def setup_source(setup_context: build_framework.SetupContext) -> bool:
    try:
        node = build_framework.pkg_unpack(setup_context, 'lua_src', LUA_SOURCES,
                                          setup_context.path.parent.ant_glob(['patches/*.*']))
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.LUA_SOURCE = node.path_from(setup_context.package_node)
        setup_context.end_msg('from source')
        return True


def setup(setup_context: build_framework.SetupContext) -> None:
    build_framework.register_setup_option(setup_context, 'lua_package')
    build_framework.start_msg_setup(setup_context)
    found = False
    if setup_context.env.PROJECTS:
        found = setup_source(setup_context)
    else:
        if not found and waflib.Options.options.lua_package in ('best', 'pkgconfig'):
            found = setup_pkgconfig(setup_context)
        if not found and waflib.Options.options.lua_package in ('best', 'system'):
            found = setup_system(setup_context)
        if not found and waflib.Options.options.lua_package in ('best', 'prebuilt'):
            found = setup_prebuilt(setup_context)
        if not found and waflib.Options.options.lua_package in ('best', 'source'):
            found = setup_source(setup_context)
    if not found:
        setup_context.end_msg('disabled', color='RED')
