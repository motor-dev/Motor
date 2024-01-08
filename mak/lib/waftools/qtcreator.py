import sys
import build_framework
from typing import Any

_VAR_PATTERN = '${%s}' if sys.platform != 'win32' else '%%%s%%'


def _to_var(name: str) -> str:
    return _VAR_PATTERN % name


class QtCreator(build_framework.ProjectGenerator):
    cmd = '_qtcreator'

    def __init__(self, **kw: Any) -> None:
        build_framework.BuildContext.__init__(self, **kw)
        self.motor_groups.append('qtcreator')

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = ['qtcreator']

        self.env.VARIANT = _to_var('Variant')
        self.env.TOOLCHAIN = _to_var('Toolchain')
        self.env.PREFIX = _to_var('Prefix')
        self.env.DEPLOY_ROOTDIR = _to_var('Deploy_RootDir')
        self.env.DEPLOY_BINDIR = _to_var('Deploy_BinDir')
        self.env.DEPLOY_RUNBINDIR = _to_var('Deploy_RunBinDir')
        self.env.DEPLOY_LIBDIR = _to_var('Deploy_LibDir')
        self.env.DEPLOY_INCLUDEDIR = _to_var('Deploy_IncludeDir')
        self.env.DEPLOY_DATADIR = _to_var('Deploy_DataDir')
        self.env.DEPLOY_PLUGINDIR = _to_var('Deploy_PluginDir')
        self.env.DEPLOY_KERNELDIR = _to_var('Deploy_KernelDir')
        build_framework.add_feature(self, 'GUI')


class Qbs(QtCreator):
    cmd = 'qbs'
    variant = 'qcmake'

    def __init__(self, **kw: Any) -> None:
        QtCreator.__init__(self, **kw)
        self.motor_groups.append('qbs')

    def load_envs(self) -> None:
        QtCreator.load_envs(self)
        self.env.PROJECTS = ['qbs', 'qtcreator']


class QCMake(QtCreator):
    cmd = 'qcmake'
    variant = 'qcmake'

    def __init__(self, **kw: Any) -> None:
        QtCreator.__init__(self, **kw)
        self.motor_groups.append('cmake')
        self.motor_groups.append('qcmake')

    def load_envs(self) -> None:
        QtCreator.load_envs(self)
        self.env.PROJECTS = ['cmake', 'qcmake', 'qtcreator']


def build(build_context: build_framework.BuildContext) -> None:
    build_context.recurse('mak/lib/waftools/build/cmake.py')
    build_context.recurse('mak/lib/waftools/build/qtcreator.py')
