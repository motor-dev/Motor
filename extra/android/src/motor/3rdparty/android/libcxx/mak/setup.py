import os

import build_framework
import waflib.Errors
import waflib.TaskGen

LIBCPP_BINARY = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/libc++-%(platform)s-%(arch)s-%(abi)s.tgz'


@waflib.TaskGen.feature('cxxtest')
def cxx_link_libcpp(task_gen: waflib.TaskGen.task_gen) -> None:
    if task_gen.env['check_libc++']:
        task_gen.env.append_value('LIB', task_gen.env['check_libc++_libs'])
        task_gen.env.append_value('LIBPATH', task_gen.env['check_libc++_libpath'])


def setup(setup_context: build_framework.SetupContext) -> None:
    build_framework.start_msg_setup(setup_context)
    try:
        node = build_framework.pkg_unpack(setup_context, 'libcpp_%(platform)s_%(arch)s_%(abi)s', LIBCPP_BINARY)
        paths = [os.path.join(node.abspath(), 'bin.%s' % a) for a in setup_context.env.VALID_ARCHITECTURES]
        paths += [os.path.join(node.abspath(), 'lib.%s' % a) for a in setup_context.env.VALID_ARCHITECTURES]
        paths = [p for p in paths if os.path.isdir(p)]
        if not build_framework.check_package(
                setup_context,
                ['c++'],
                node,
                includepath=[setup_context.path.parent.make_node('api').abspath()],
                libpath=paths,
                var='libcxx'
        ):
            raise waflib.Errors.WafError('package not setup')
    except waflib.Errors.WafError as e:
        setup_context.end_msg(str(e), color='RED')
    else:
        setup_context.env.LIBCPP_BINARY = node.path_from(setup_context.package_node)
        setup_context.end_msg('from prebuilt')
