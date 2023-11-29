import build_framework
import waftools_common.cmake
from typing import Any, List, Optional, Tuple


class CMake(build_framework.ProjectGenerator):
    """
        Creates CMake project structure.
    """
    cmd = 'cmake'
    variant = 'cmake'

    def __init__(self, **kw: Any) -> None:
        build_framework.BuildContext.__init__(self, **kw)

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = [self.__class__.cmd]

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

    def execute(self) -> Optional[str]:
        result = build_framework.ProjectGenerator.execute(self)
        if result is not None:
            return result

        self.write_workspace()
        return None

    def write_workspace(self) -> List[Tuple[str, str]]:
        return waftools_common.cmake.write_cmake_workspace(self)
