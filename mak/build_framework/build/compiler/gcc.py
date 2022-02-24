def build(bld):
    if bld.env.COMPILER_NAME == 'gcc':
        for env in bld.multiarch_envs:
            env.ENABLE_COMPILER_DEPS = True
            env.append_unique('CFLAGS', ['-MMD'])
            env.append_unique('CXXFLAGS', ['-MMD'])
