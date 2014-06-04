from waflib import Errors

def options(opt):
    pass

def setup(conf):
    pass

def setup_python(conf):
    if 'windows' in conf.env.VALID_PLATFORMS:
        pass
    else:
        raise Errors.WafError('python 2.6 not available')

def build(bld):
    if 'windows' in bld.env.VALID_PLATFORMS:
        bld.thirdparty('3rdparty.python26', bld.env,
                       defines=['PYTHON_LIBRARY="python26"'])
    else:
        raise Errors.WafError('python not available')
