import build_framework
import waflib.Errors
import waflib.Options

BULLET_SOURCES = 'https://github.com/bulletphysics/bullet3/archive/2.87.tar.gz'
BULLET_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/' \
                  'bullet-2.87-%(platform)s-%(arch)s-%(abi)s.tgz'


def setup_pkgconfig(setup_context: build_framework.SetupContext) -> bool:
    if setup_context.env.CXX_NAME != 'sun':  # sunCC does not have the same ABI on Linux
        try:
            build_framework.pkg_config(setup_context, 'bullet')
        except waflib.Errors.WafError:
            return False
        else:
            setup_context.env.BULLET_BINARY = True
            setup_context.end_msg('from pkg-config')
            return True
    else:
        return False


def setup_system(setup_context: build_framework.SetupContext) -> bool:
    if 'windows' not in setup_context.env.VALID_PLATFORMS and setup_context.env.CXX_NAME != 'sun' and \
            build_framework.check_lib(
                setup_context,
                ['BulletSoftBody', 'BulletDynamics', 'BulletCollision', 'LinearMath'],
                var='bullet',
                includepath=['=/usr/include/bullet', '=/usr/local/include/bullet'],
                includes=[
                    'LinearMath/btAlignedAllocator.h', 'btBulletDynamicsCommon.h',
                    'BulletCollision/BroadphaseCollision/btDbvt.h'
                ],
                functions=['btAlignedAllocSetCustom']
            ):
        setup_context.env.BULLET_BINARY = True
        setup_context.end_msg('from system')
        return True
    else:
        return False


def setup_prebuilt(setup_context: build_framework.SetupContext) -> bool:
    try:
        bullet_node = build_framework.pkg_unpack(setup_context, 'bullet_bin_%(platform)s-%(arch)s-%(abi)s',
                                                 BULLET_BINARIES)
        if not build_framework.check_package(setup_context, ['motor.3rdparty.physics.bullet'], bullet_node,
                                             var='bullet'):
            raise waflib.Errors.WafError('using bullet from source')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.BULLET_BINARY = bullet_node.path_from(setup_context.package_node)
        setup_context.end_msg('from prebuilt')
        return True


def setup_source(setup_context: build_framework.SetupContext) -> bool:
    try:
        bullet_node = build_framework.pkg_unpack(setup_context, 'bullet_src', BULLET_SOURCES,
                                                 [
                                                     setup_context.path.parent.make_node(
                                                         'patches/bullet3-2.87-vec4copy.diff'),
                                                     setup_context.path.parent.make_node(
                                                         'patches/bullet3-2.87-shuffle.diff'),
                                                     setup_context.path.parent.make_node('patches/bullet3-2.87.diff'),
                                                 ])
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.BULLET_SOURCE = bullet_node.path_from(setup_context.package_node)
        setup_context.end_msg('from source')
        return True


def setup(setup_context: build_framework.SetupContext) -> None:
    build_framework.register_setup_option(setup_context, 'bullet_package')
    found = False
    build_framework.start_msg_setup(setup_context)
    if setup_context.env.PROJECTS:
        found = setup_source(setup_context)
    else:
        if not found and waflib.Options.options.bullet_package in ('best', 'pkgconfig'):
            found = setup_pkgconfig(setup_context)
        if not found and waflib.Options.options.bullet_package in ('best', 'system'):
            found = setup_system(setup_context)
        if not found and waflib.Options.options.bullet_package in ('best', 'prebuilt'):
            found = setup_prebuilt(setup_context)
        if not found and waflib.Options.options.bullet_package in ('best', 'source'):
            found = setup_source(setup_context)
    if not found:
        setup_context.end_msg('disabled', color='RED')
