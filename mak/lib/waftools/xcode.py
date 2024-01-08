import os
import build_framework
import waflib.Node
from typing import Any, List


class xcode(build_framework.ProjectGenerator):
    """creates projects for XCode 3.x and 4.x"""
    cmd = 'xcode'
    version = ('Xcode 3.1', 45)
    variant = 'xcode'

    def __init__(self, **kw: Any) -> None:
        build_framework.ProjectGenerator.__init__(self, **kw)
        self.motor_groups.append('xcode')

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = [self.__class__.cmd]
        self.env.TOOLCHAIN = '$(TOOLCHAIN)'
        self.env.VARIANT = '$(CONFIG)'
        self.env.PREFIX = '$(PREFIX)'
        self.env.DEPLOY_ROOTDIR = '$(DEPLOY_ROOTDIR)'
        self.env.DEPLOY_BINDIR = '$(DEPLOY_BINDIR)'
        self.env.DEPLOY_RUNBINDIR = '$(DEPLOY_RUNBINDIR)'
        self.env.DEPLOY_LIBDIR = '$(DEPLOY_LIBDIR)'
        self.env.DEPLOY_INCLUDEDIR = '$(DEPLOY_INCLUDEDIR)'
        self.env.DEPLOY_DATADIR = '$(DEPLOY_DATADIR)'
        self.env.DEPLOY_PLUGINDIR = '$(DEPLOY_PLUGINDIR)'
        self.env.DEPLOY_KERNELDIR = '$(DEPLOY_KERNELDIR)'
        build_framework.add_feature(self, 'GUI')

    def tidy_nodes(self) -> List[waflib.Node.Node]:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, os.path.basename(self.srcnode.abspath()))
        xcodeproj = self.srcnode.make_node('%s.xcodeproj' % appname)
        return xcodeproj.ant_glob('**/*')


def build(build_context: build_framework.BuildContext) -> None:
    build_context.recurse('mak/lib/waftools/build/xcode.py')
