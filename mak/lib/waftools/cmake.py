import build_framework
import waftools_common.cmake
from typing import Any, List, Optional, Tuple


class CMake(build_framework.ProjectGenerator):
    """
        Creates CMake project structure.
    """
    cmd = 'cmake'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.cmake'
    variant = 'projects/cmake'

    def __init__(self, **kw: Any) -> None:
        build_framework.BuildContext.__init__(self, **kw)

    def execute(self) -> Optional[str]:
        """
        Entry point
        """
        if build_framework.schedule_setup(self):
            return "SKIP"

        self.restore()
        if not self.all_envs:
            self.load_envs()
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

        self.recurse([self.run_dir])
        self.write_workspace()
        return None

    def write_workspace(self) -> List[Tuple[str, str]]:
        return waftools_common.cmake.write_cmake_workspace(self)
