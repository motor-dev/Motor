from ...options import BuildContext


def setup_compiler_suncc(build_context: BuildContext) -> None:
    if build_context.env.COMPILER_NAME == 'suncc':
        for env in build_context.multiarch_envs:
            env['ENABLE_COMPILER_DEPS'] = True
            env.append_unique('CFLAGS', ['-xMMD'])
            env.append_unique('CXXFLAGS', ['-xMMD'])
