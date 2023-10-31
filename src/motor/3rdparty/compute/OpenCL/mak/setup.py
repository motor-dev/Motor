import build_framework
import waflib.Errors

CL_ICD_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/OpenCL-icd-2.2-%(platform)s.tgz'


def setup(setup_context: build_framework.SetupContext) -> None:
    if setup_context.env.PROJECTS:
        setup_context.env.OPENCL_SOURCE = setup_context.path.path_from(
            setup_context.package_node)
    else:
        build_framework.start_msg_setup(setup_context)
        if setup_context.env.CLC_CXX:
            if 'posix' in setup_context.env.VALID_PLATFORMS:
                try:
                    build_framework.pkg_config(setup_context, 'OpenCL', var='OpenCL')
                except waflib.Errors.WafError as e:
                    pass
                else:
                    setup_context.env.OPENCL_BINARY = True
                    setup_context.end_msg('from pkg-config', color='GREEN')
                    return
            if build_framework.check_lib(setup_context, ['OpenCL'], var='OpenCL'):
                setup_context.env.OPENCL_BINARY = True
                setup_context.end_msg('from system', color='GREEN')
                return
            try:
                cl_node = build_framework.pkg_unpack(setup_context, 'cl_bin_%(platform)s', CL_ICD_BINARIES)
                if not build_framework.check_package(
                        setup_context,
                        ['OpenCL'],
                        cl_node,
                        var='OpenCL',
                        includepath=[setup_context.path.parent.make_node('api').abspath()],
                        includes=['CL/cl.h'],
                        functions=['clCreateKernel']
                ):
                    raise waflib.Errors.WafError('no OpenCL')
                setup_context.env.OPENCL_BINARY = cl_node.path_from(setup_context.package_node)
                setup_context.end_msg('from prebuilt', color='GREEN')
            except waflib.Errors.WafError:
                setup_context.end_msg('not found', color='YELLOW')
        else:
            setup_context.end_msg('not found', color='YELLOW')
