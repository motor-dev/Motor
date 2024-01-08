import build_framework
import waflib.Node
from typing import Any, List


class vscode_common(build_framework.ProjectGenerator):
    """creates common plumbing for VSCode projects"""
    cmd = '_vscode'

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

    def tidy_nodes(self) -> List[waflib.Node.Node]:
        return self.srcnode.ant_glob('.vscode/*')


class vscode(vscode_common):
    """creates projects for Visual Studio Code"""
    cmd = 'vscode'
    variant = 'vscode'
    extensions = ['"ms-vscode.cpptools"', '"ms-python.python"', '"eeyore.yapf"', '"ms-python.mypy-type-checker"']

    def __init__(self, **kw: Any) -> None:
        vscode_common.__init__(self, **kw)
        self.motor_groups.append('vscode')


class vscode_cmake(vscode_common):
    """creates projects for Visual Studio Code using CMake"""
    cmd = 'vscode-cmake'
    variant = 'vscode-cmake'
    extensions = [
        '"ms-vscode.cpptools"', '"ms-python.python"', '"eeyore.yapf"', '"ms-python.mypy-type-checker"',
        '"ms-vscode.cmake-tools"'
    ]

    def __init__(self, **kw: Any) -> None:
        vscode_common.__init__(self, **kw)
        self.motor_groups.append('cmake')
        self.motor_groups.append('vscode-cmake')

    def load_envs(self) -> None:
        vscode_common.load_envs(self)
        self.env.append_value('PROJECTS', 'cmake')
        self.env.append_value('PROJECTS', 'vscode-cmake')


def build(build_context: build_framework.BuildContext) -> None:
    build_context.recurse('mak/lib/waftools/build/cmake.py')
    build_context.recurse('mak/lib/waftools/build/vscode.py')
