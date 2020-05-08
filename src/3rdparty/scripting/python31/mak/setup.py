from waflib import Errors
import os


def setup(conf):
    pass


def setup_python(conf):
    if 'windows' in conf.env.VALID_PLATFORMS:
        for a in conf.env.VALID_ARCHITECTURES:
            if os.path.isdir(os.path.join(conf.path.abspath(), 'bin.windows.%s' % a)):
                conf.env.check_python31 = True
                conf.env.check_python31_defines = ['PYTHON_LIBRARY=python31']
                break
        else:
            raise Errors.WafError('%s not available for windows %s' % (conf.path.name,
                                                                       conf.env.VALID_ARCHITECTURES[0]))
    else:
        raise Errors.WafError('%s not available' % conf.path.name)