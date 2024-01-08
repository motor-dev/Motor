import build_framework
import waflib.Node
from typing import Any, List


class CLion(build_framework.ProjectGenerator):
    """
        creates projects for IntelliJ CLion
    """
    cmd = 'clion'
    variant = 'clion'

    def __init__(self, **kw: Any) -> None:
        build_framework.ProjectGenerator.__init__(self, **kw)
        self.motor_groups.append('cmake')
        self.motor_groups.append('clion')

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = ['cmake', self.__class__.cmd]

        self.env.VARIANT = '${input:motor-Variant}'
        self.env.TOOLCHAIN = '${input:motor-Toolchain}'
        self.env.PREFIX = '${input:motor-Prefix}'
        self.env.TMPDIR = '${input:motor-TmpDir}'
        self.env.DEPLOY_ROOTDIR = '${input:motor-Deploy_RootDir}'
        self.env.DEPLOY_BINDIR = '${input:motor-Deploy_BinDir}'
        self.env.DEPLOY_RUNBINDIR = '${input:motor-Deploy_RunBinDir}'
        self.env.DEPLOY_LIBDIR = '${input:motor-Deploy_LibDir}'
        self.env.DEPLOY_INCLUDEDIR = '${input:motor-Deploy_IncludeDir}'
        self.env.DEPLOY_DATADIR = '${input:motor-Deploy_DataDir}'
        self.env.DEPLOY_PLUGINDIR = '${input:motor-Deploy_PluginDir}'
        self.env.DEPLOY_KERNELDIR = '${input:motor-Deploy_KernelDir}'
        build_framework.add_feature(self, 'GUI')

    def tidy_nodes(self) -> List[waflib.Node.Node]:
        return self.srcnode.ant_glob('.idea/runConfigurations/motor_*')


def build(build_context: build_framework.BuildContext) -> None:
    build_context.recurse('mak/lib/waftools/build/cmake.py')
    build_context.recurse('mak/lib/waftools/build/clion.py')
