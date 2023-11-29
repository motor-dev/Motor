import build_framework


def setup(setup_context: build_framework.SetupContext) -> None:
    env = setup_context.env
    if not env.PROJECTS:
        build_framework.start_msg_setup(setup_context)
        setup_context.end_msg(
            ', '.join([(env.ARCH_NAME + variant) for variant in env.VECTOR_OPTIM_VARIANTS]), color='GREEN'
        )
        env.append_value('KERNEL_TOOLCHAINS', [('cpu', env.TOOLCHAIN)])
        env.append_unique('DEFINES', [
            'MOTOR_VECTOR_OPTIM_VARIANTS="%s"' % '+'.join(
                [env.ARCH_NAME + optim for optim in env.VECTOR_OPTIM_VARIANTS])])
