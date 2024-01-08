import build_framework


def setup(setup_context: build_framework.SetupContext) -> None:
    if setup_context.env.check_CUDA:
        include_dir = setup_context.path.parent.make_node('api.cuda').abspath()
        setup_context.env.append_value(
            'CUDA_KERNEL_HEADER_PATH', [include_dir]
        )
        setup_context.env.append_value('NVCC_CXXFLAGS', ['-I%s' % include_dir])
