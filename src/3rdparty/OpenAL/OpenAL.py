import os

def options(opt):
    pass

def setup(conf):
    if 'darwin' in conf.env.VALID_PLATFORMS:
        conf.check_framework('OpenAL', var='ALFramework')
    else:
        conf.check_lib('openal', var='OpenAL', libpath=[os.path.join(conf.path.abspath(), 'lib.%s.%s'%(conf.env.VALID_PLATFORMS[0], a)) for a in conf.env.VALID_ARCHITECTURES])

def build(bld):
    for env in bld.multiarch_envs:
        if env.ALFramework or  env.OpenAL or bld.env.PROJECTS:
            bld.thirdparty('3rdparty.OpenAL', env, libs=env.OpenAL, frameworks=env.ALFramework)
            env.append_unique('FEATURES', ['OpenAL'])