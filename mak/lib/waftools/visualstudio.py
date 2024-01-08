import build_framework
from typing import Any


class VisualStudio(build_framework.ProjectGenerator):
    cmd = '_vs'

    def __init__(self, **kw: Any) -> None:
        build_framework.ProjectGenerator.__init__(self, **kw)
        self.motor_groups.append(self.cmd)

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = ['visualstudio', self.__class__.cmd]

        self.env.VARIANT = '$(Variant)'
        self.env.TOOLCHAIN = '$(Toolchain)'
        self.env.PREFIX = '$(Prefix)'
        self.env.TMPDIR = '$(TmpDir)'
        self.env.DEPLOY_ROOTDIR = '$(Deploy_RootDir)'
        self.env.DEPLOY_BINDIR = '$(Deploy_BinDir)'
        self.env.DEPLOY_RUNBINDIR = '$(Deploy_RunBinDir)'
        self.env.DEPLOY_LIBDIR = '$(Deploy_LibDir)'
        self.env.DEPLOY_INCLUDEDIR = '$(Deploy_IncludeDir)'
        self.env.DEPLOY_DATADIR = '$(Deploy_DataDir)'
        self.env.DEPLOY_PLUGINDIR = '$(Deploy_PluginDir)'
        self.env.DEPLOY_KERNELDIR = '$(Deploy_KernelDir)'
        build_framework.add_feature(self, 'GUI')


class vs2017(VisualStudio):
    """creates projects for Visual Studio 2017"""
    cmd = 'vs2017'
    variant = 'vs2017'
    version = (('Visual Studio 15', '12.00', '15.0.00000.0'), ('6.0', '14.1', '15.0'))


class vs2019(VisualStudio):
    """creates projects for Visual Studio 2019"""
    cmd = 'vs2019'
    variant = 'vs2019'
    version = (('Visual Studio 16', '12.00', '16.0.00000.0'), ('6.0', '14.2', '16.0'))


class vs2022(VisualStudio):
    """creates projects for Visual Studio 2022"""
    cmd = 'vs2022'
    variant = 'vs2022'
    version = (('Visual Studio 17', '12.00', '17.0.00000.0'), ('6.0', '14.3', '17.0'))


class vs_cmake(build_framework.ProjectGenerator):
    """creates projects for Visual Studio using CMake"""
    cmd = 'vs-cmake'
    variant = 'vs-cmake'

    def __init__(self, **kw: Any) -> None:
        build_framework.ProjectGenerator.__init__(self, **kw)
        self.motor_groups.append('vs-cmake')
        self.motor_groups.append('cmake')

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = ['cmake', self.__class__.cmd]

        self.env.VARIANT = '${env.Variant}'
        self.env.TOOLCHAIN = '${env.Toolchain}'
        self.env.PREFIX = '${env.Prefix}'
        self.env.TMPDIR = '${env.TmpDir}'
        self.env.DEPLOY_ROOTDIR = '${env.Deploy_RootDir}'
        self.env.DEPLOY_BINDIR = '${env.Deploy_BinDir}'
        self.env.DEPLOY_RUNBINDIR = '${env.Deploy_RunBinDir}'
        self.env.DEPLOY_LIBDIR = '${env.Deploy_LibDir}'
        self.env.DEPLOY_INCLUDEDIR = '${env.Deploy_IncludeDir}'
        self.env.DEPLOY_DATADIR = '${env.Deploy_DataDir}'
        self.env.DEPLOY_PLUGINDIR = '${env.Deploy_PluginDir}'
        self.env.DEPLOY_KERNELDIR = '${env.Deploy_KernelDir}'
        build_framework.add_feature(self, 'GUI')


def build(build_context: build_framework.BuildContext) -> None:
    build_context.recurse('mak/lib/waftools/build/cmake.py')
    build_context.recurse('mak/lib/waftools/build/visualstudio.py')
