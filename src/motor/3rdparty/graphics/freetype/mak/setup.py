import build_framework
import waflib.Errors
import waflib.Options

FT_SOURCES = 'https://download.savannah.gnu.org/releases/freetype/freetype-2.10.2.tar.gz'
FT_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/' \
              'freetype-2.10.2-%(platform)s-%(arch)s-%(abi)s.tgz'


def setup_pkgconfig(setup_context: build_framework.SetupContext) -> bool:
    try:
        build_framework.pkg_config(setup_context, 'freetype2', var='freetype')
    except waflib.Errors.WafError as e:
        return False
    else:
        setup_context.env.FREETYPE_BINARY = True
        setup_context.end_msg('from pkg-config')
        return True


def setup_system(setup_context: build_framework.SetupContext) -> bool:
    if 'windows' not in setup_context.env.VALID_PLATFORMS and build_framework.check_lib(
            setup_context,
            ['freetype'],
            var='freetype',
            includes=['ft2build.h', 'freetype/freetype.h', 'freetype/t1tables.h'],
            includepath=['=/usr/include/freetype2', '=/usr/local/include/freetype2'],
            functions=['FT_Get_PS_Font_Info']
    ):
        setup_context.env.FREETYPE_BINARY = True
        setup_context.end_msg('from system')
        return True
    return False


def setup_prebuilt(setup_context: build_framework.SetupContext) -> bool:
    try:
        freetype_node = build_framework.pkg_unpack(setup_context, 'freetype_bin_%(platform)s-%(arch)s-%(abi)s',
                                                   FT_BINARIES)
        if not build_framework.check_package(
                setup_context,
                ['motor.3rdparty.system.freetype'],
                freetype_node,
                var='freetype',
                includes=['ft2build.h', 'freetype/freetype.h', 'freetype/t1tables.h'],
                functions=['FT_Get_PS_Font_Info']
        ):
            raise waflib.Errors.WafError('using freetype from source')
        setup_context.env.FREETYPE_BINARY = freetype_node.path_from(setup_context.package_node)
        setup_context.end_msg('from prebuilt')
        return True
    except waflib.Errors.WafError:
        return False


def setup_source(setup_context: build_framework.SetupContext) -> bool:
    try:
        freetype_node = build_framework.pkg_unpack(setup_context, 'freetype_src', FT_SOURCES)
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.FREETYPE_SOURCE = freetype_node.path_from(setup_context.package_node)
        setup_context.end_msg('from source')
        return True


def setup(setup_context: build_framework.SetupContext) -> None:
    build_framework.register_setup_option(setup_context, 'freetype_package')
    build_framework.start_msg_setup(setup_context)
    if setup_context.env.PROJECTS:
        if not setup_source(setup_context):
            setup_context.end_msg('disabled', color='RED')
    else:
        found = False
        if waflib.Options.options.freetype_package in ('best', 'pkgconfig'):
            found = setup_pkgconfig(setup_context)
        if not found and waflib.Options.options.freetype_package in ('best', 'system'):
            found = setup_system(setup_context)
        if not found and waflib.Options.options.freetype_package in ('best', 'prebuilt'):
            found = setup_prebuilt(setup_context)
        if not found and waflib.Options.options.freetype_package in ('best', 'source'):
            found = setup_source(setup_context)
        if not found:
            setup_context.end_msg('disabled', color='RED')
