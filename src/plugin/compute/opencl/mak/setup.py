import build_framework


def setup(setup_context: build_framework.SetupContext) -> None:
    if setup_context.env.check_OpenCL:
        setup_context.env.append_value('KERNEL_TOOLCHAINS', [('opencl', setup_context.env.TOOLCHAIN)])
        setup_context.env.append_value(
            'CLC_KERNEL_HEADER_PATH', [setup_context.path.parent.make_node('api.cl').abspath()]
        )
