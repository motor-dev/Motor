import os
from be_typing import TYPE_CHECKING


def setup(conf):
    # type: (Configure.ConfigurationContext) -> None
    "setup step before the build: recursively calls setup on every third party library"
    extra = conf.bugenginenode.make_node('extra')
    if conf.env.VALID_PLATFORMS:
        extra_dir = os.path.join(extra.abspath(), conf.env.VALID_PLATFORMS[0])
        if os.path.isdir(extra_dir):
            conf.recurse(extra_dir, once=False)


def multiarch_setup(conf):
    # type: (Configure.ConfigurationContext) -> None
    conf.recurse('checks.py')
    conf.fun = 'setup'
    if conf.env.SUB_TOOLCHAINS:
        for t in conf.env.SUB_TOOLCHAINS:
            try:
                conf.start_msg('Setting up environment')
                conf.end_msg(t)
                conf.setenv(t + '.setup', conf.all_envs[t])
                conf.recurse(conf.run_dir, once=False)
            except Exception as e:
                raise
            else:
                conf.env.BUGENGINE_SETUP = True
            finally:
                conf.setenv(conf.bugengine_variant)
        conf.setenv(conf.bugengine_variant + '.setup', conf.all_envs[conf.bugengine_variant])
        conf.env.BUGENGINE_SETUP = True
    else:
        t = conf.bugengine_variant
        try:
            conf.start_msg('Setting up environment')
            conf.end_msg(t)
            conf.setenv(t + '.setup', conf.all_envs[t])
            conf.recurse(conf.run_dir, once=False)
        except Exception as e:
            raise
        else:
            conf.env.BUGENGINE_SETUP = True


if TYPE_CHECKING:
    from waflib import Configure
