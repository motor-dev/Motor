import build_framework
import waflib.Errors
import waflib.Options

ZLIB_SOURCES = 'https://zlib.net/fossils/zlib-1.2.12.tar.gz'
ZLIB_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/' \
                'zlib-1.2.11-%(platform)s-%(arch)s-%(abi)s.tgz'
MINIZIP_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/' \
                   'minizip-1.2.11-%(platform)s-%(arch)s-%(abi)s.tgz'


def setup_pkgconfig_zlib(setup_context: build_framework.SetupContext) -> bool:
    try:
        build_framework.pkg_config(setup_context, 'zlib', var='zlib')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.ZLIB_BINARY = True
        setup_context.end_msg('from pkg-config')
        return True


def setup_pkgconfig_minizip(setup_context: build_framework.SetupContext) -> bool:
    try:
        build_framework.pkg_config(setup_context, 'minizip', var='minizip')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.MINIZIP_BINARY = True
        setup_context.end_msg('from pkg-config')
        return True


def setup_system_zlib(setup_context: build_framework.SetupContext) -> bool:
    if 'windows' not in setup_context.env.VALID_PLATFORMS and build_framework.check_lib(
            setup_context,
            ['z'],
            var='zlib',
            includes=['zlib.h'],
            functions=['deflate']
    ):
        setup_context.env.ZLIB_BINARY = True
        setup_context.end_msg('from system')
        return True
    else:
        return False


def setup_system_minizip(setup_context: build_framework.SetupContext) -> bool:
    if 'windows' not in setup_context.env.VALID_PLATFORMS and build_framework.check_lib(
            setup_context,
            ['minizip'],
            var='minizip',
            includepath=['=/usr/include/minizip', '=/usr/local/include/minizip'],
            includes=['unzip.h'],
            functions=['unzClose']
    ):
        setup_context.env.MINIZIP_BINARY = True
        setup_context.end_msg('from system')
        return True
    else:
        return False


def setup_prebuilt_zlib(setup_context: build_framework.SetupContext) -> bool:
    try:
        zlib_node = build_framework.pkg_unpack(
            setup_context,
            'zlib_bin_%(platform)s-%(arch)s-%(abi)s',
            ZLIB_BINARIES
        )
        if not build_framework.check_package(
                setup_context,
                ['motor.3rdparty.system.zlib'],
                zlib_node,
                var='zlib'
        ):
            raise waflib.Errors.WafError('using zlib from source')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.ZLIB_BINARY = zlib_node.path_from(setup_context.package_node)
        setup_context.end_msg('from prebuilt')
        return True


def setup_prebuilt_minizip(setup_context: build_framework.SetupContext) -> bool:
    try:
        minizip_node = build_framework.pkg_unpack(
            setup_context,
            'minizip_bin_%(platform)s-%(arch)s-%(abi)s',
            MINIZIP_BINARIES
        )
        if not build_framework.check_package(
                setup_context,
                ['motor.3rdparty.system.minizip'],
                minizip_node,
                var='minizip'
        ):
            raise waflib.Errors.WafError('using minizip from source')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.MINIZIP_BINARY = minizip_node.path_from(setup_context.package_node)
        setup_context.end_msg('from prebuilt')
        return True


def setup_source_zlib(setup_context: build_framework.SetupContext) -> bool:
    try:
        setup_context.env.ZLIB_SOURCE = build_framework.pkg_unpack(
            setup_context,
            'zlib_src',
            ZLIB_SOURCES,
            setup_context.path.parent.ant_glob(['patches/*.*'])
        ).path_from(setup_context.package_node)
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.end_msg('from source')
        return True


def setup_source_minizip(setup_context: build_framework.SetupContext) -> bool:
    try:
        setup_context.env.MINIZIP_SOURCE = build_framework.pkg_unpack(
            setup_context,
            'zlib_src',
            ZLIB_SOURCES,
            setup_context.path.parent.ant_glob(['patches/*.*'])
        ).path_from(setup_context.package_node)
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.end_msg('from source')
        return True


def setup(setup_context: build_framework.SetupContext) -> None:
    build_framework.register_setup_option(setup_context, 'zlib_package')
    build_framework.register_setup_option(setup_context, 'minizip_package')
    build_framework.start_msg_setup(setup_context, 'zlib')
    found = False
    if setup_context.env.PROJECTS:
        found = setup_source_zlib(setup_context)
    else:
        if not found and waflib.Options.options.zlib_package in ('best', 'pkgconfig'):
            found = setup_pkgconfig_zlib(setup_context)
        if not found and waflib.Options.options.zlib_package in ('best', 'system'):
            found = setup_system_zlib(setup_context)
        if not found and waflib.Options.options.zlib_package in ('best', 'prebuilt'):
            found = setup_prebuilt_zlib(setup_context)
        if not found and waflib.Options.options.zlib_package in ('best', 'source'):
            found = setup_source_zlib(setup_context)
    if not found:
        setup_context.end_msg('disabled', color='RED')

    build_framework.start_msg_setup(setup_context, 'minizip')
    found = False
    if setup_context.env.PROJECTS:
        found = setup_source_minizip(setup_context)
    else:
        if not found and waflib.Options.options.minizip_package in ('best', 'pkgconfig'):
            found = setup_pkgconfig_minizip(setup_context)
        if not found and waflib.Options.options.minizip_package in ('best', 'system'):
            found = setup_system_minizip(setup_context)
        if not found and waflib.Options.options.minizip_package in ('best', 'prebuilt'):
            found = setup_prebuilt_minizip(setup_context)
        if not found and waflib.Options.options.minizip_package in ('best', 'source'):
            found = setup_source_minizip(setup_context)
    if not found:
        setup_context.end_msg('disabled', color='RED')
