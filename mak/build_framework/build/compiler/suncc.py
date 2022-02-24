def build(bld):
    if bld.env.COMPILER_NAME == 'suncc':
        for env in bld.multiarch_envs:
            env.ENABLE_COMPILER_DEPS = True
            env.append_unique('CFLAGS', ['-xMMD'])
            env.append_unique('CXXFLAGS', ['-xMMD'])
