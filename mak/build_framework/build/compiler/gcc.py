def build(bld):
    for env in bld.multiarch_envs:
        if env.COMPILER_NAME == 'gcc':
            env.ENABLE_COMPILER_DEPS = True
            env.append_unique('CFLAGS', ['-MMD'])
            env.append_unique('CXXFLAGS', ['-MMD'])
