from ...options import BuildContext


def setup_compiler_gcc(build_context: BuildContext) -> None:
    for env in build_context.multiarch_envs:
        if env.COMPILER_NAME == 'gcc':
            env['ENABLE_COMPILER_DEPS'] = True
            env.append_unique('CFLAGS', ['-MMD'])
            env.append_unique('CXXFLAGS', ['-MMD'])
