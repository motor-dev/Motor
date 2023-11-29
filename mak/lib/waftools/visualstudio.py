import os
import sys
import json
import xml.dom.minidom
import waflib.Context
import waflib.Errors
import waflib.Node
import waflib.TaskGen
import waflib.Logs
import build_framework
import waftools_common.cmake
from waftools_common.utils import path_from, gather_includes_defines, generate_guid
from typing import Dict, List, Optional, Tuple, Union


def _set_attributes(element: xml.dom.minidom.Element, attrs: Dict[str, str]) -> None:
    for k, v in attrs.items():
        element.setAttribute(k, v)


class XmlFile:

    def __init__(self) -> None:
        self.document = xml.dom.minidom.Document()

    def add(
            self,
            node: xml.dom.minidom.Node,
            child_node: str,
            value: Union[None, str, Dict[str, str]] = None
    ) -> xml.dom.minidom.Element:
        el = self.document.createElement(child_node)
        if value is not None:
            if isinstance(value, str):
                el.appendChild(self.document.createTextNode(value))
            elif isinstance(value, dict):
                _set_attributes(el, value)
        node.appendChild(el)
        return el

    def write(self, node: waflib.Node.Node, indent: str = '\t') -> None:
        try:
            xml_text = node.read()
        except IOError:
            xml_text = ''
        newxml = self.document.toprettyxml(indent=indent)
        if xml_text != newxml:
            waflib.Logs.pprint('NORMAL', 'writing %s' % node.name)
            node.write(newxml)


class Solution:

    def __init__(
            self, bld: build_framework.BuildContext, version_number: str, version_name: str, use_folders: bool,
            vstudio_ide_version: str
    ) -> None:
        self.header = '\xef\xbb\xbf\r\nMicrosoft Visual Studio Solution File, Format Version %s\r\n# %s' % (
            version_number, version_name
        )
        if vstudio_ide_version:
            self.header += '\r\nVisualStudioVersion = %s\r\nMinimumVIsualStudioVersion = %s' % (
                vstudio_ide_version, vstudio_ide_version
            )
        self.projects = []  # type: List[str]
        self.project_configs = []  # type: List[str]
        self.configs = [
            '\t\t%s|%s = %s|%s' % (v, t, v, t) for v in bld.env.ALL_VARIANTS for t in bld.env.ALL_TOOLCHAINS
        ]
        self.folders = []  # type: List[Tuple[str, str]]
        self.folders_made = {}  # type: Dict[str, str]
        self.use_folders = use_folders
        self.master = ''

    def add_folder(self, name: str) -> Optional[str]:
        names = name.split('.')[:-1]
        if names:
            folder_name = '.'.join(names)
            try:
                folder = self.folders_made[folder_name]
            except KeyError:
                folder = generate_guid('folder:' + folder_name)
                self.folders_made[folder_name] = folder
                self.projects.append(
                    'Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "%s", "%s", "%s"\r\nEndProject' %
                    (names[-1], names[-1], folder)
                )
                parent = self.add_folder(folder_name)
                if parent:
                    self.folders.append((folder, parent))
            return folder
        else:
            return None

    def add(
            self, task_gen: waflib.TaskGen.task_gen, project: "VCxproj", project_path: str, build: bool = False
    ) -> None:
        assert isinstance(task_gen.bld, VisualStudio)
        self.projects.append(
            'Project("%s") = "%s", "%s", "%s"\r\nEndProject' % (project.GUID, project.name, project_path, project.guid)
        )
        project_config = []
        for t in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[t]
            platform = task_gen.bld.get_platform(env.MS_PROJECT_PLATFORM)
            project_config += [
                '\t\t%s.%s|%s.ActiveCfg = %s-%s|%s' % (project.guid, v, t, t, v, platform)
                for v in task_gen.bld.env.ALL_VARIANTS
            ]
            if build:
                self.master = project.guid
                project_config += [
                    '\t\t%s.%s|%s.Build.0 = %s-%s|%s' % (project.guid, v, t, t, v, platform)
                    for v in task_gen.bld.env.ALL_VARIANTS
                ]
        self.project_configs += project_config
        if self.use_folders:
            parent = self.add_folder(getattr(task_gen, 'project_name'))
            if parent:
                self.folders.append((project.guid, parent))

    def write(self, node: waflib.Node.Node) -> None:
        nested_projects = ''
        if self.use_folders:
            nested_projects = '\tGlobalSection(NestedProjects) = preSolution\r\n%s\n\tEndGlobalSection\r\n' % \
                              '\r\n'.join(
                                  ['\t\t%s = %s' % (project, parent) for project, parent in self.folders]
                              )
        newsolution = '%s\r\n' \
                      '%s\r\n' \
                      'Global\r\n' \
                      '\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\r\n' \
                      '%s\r\n' \
                      '\tEndGlobalSection\r\n' \
                      '\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\r\n' \
                      '%s\r\n' \
                      '\tEndGlobalSection\r\n' \
                      '%sEndGlobal\r\n' % (
                          self.header, '\n'.join(self.projects), '\n'.join(self.configs),
                          '\r\n'.join(self.project_configs
                                      ), nested_projects
                      )
        try:
            solution = node.read()
        except IOError:
            solution = ''
        if solution != newsolution:
            waflib.Logs.pprint('NORMAL', 'writing %s' % node.name)
            node.write(newsolution)


class VCxproj:
    GUID = '{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}'
    extensions = ['vcxproj', 'vcxproj.filters']

    def __init__(
            self, task_gen: waflib.TaskGen.task_gen, version: str, version_project: Tuple[str, str, str],
            use_folders: bool
    ) -> None:
        assert isinstance(task_gen.bld, VisualStudio)
        assert task_gen.bld.launcher is not None
        options = [a for a in sys.argv if a[0] == '-']
        self.vcxproj = XmlFile()
        self.vcxfilters = XmlFile()
        if use_folders:
            self.name = task_gen.target.split('.')[-1]
        else:
            self.name = task_gen.target
        project = self.vcxfilters.add(
            self.vcxfilters.document, 'Project', {
                'DefaultTargets': 'Build',
                'ToolsVersion': version_project[2],
                'xmlns': 'http://schemas.microsoft.com/developer/msbuild/2003'
            }
        )
        self.filter_nodes = self.vcxfilters.add(project, 'ItemGroup')
        self.file_nodes = self.vcxfilters.add(project, 'ItemGroup')

        self.guid = generate_guid('target:' + task_gen.target)
        project = self.vcxproj.add(
            self.vcxproj.document, 'Project', {
                'DefaultTargets': 'Build',
                'ToolsVersion': version_project[2],
                'xmlns': 'http://schemas.microsoft.com/developer/msbuild/2003'
            }
        )
        configs = self.vcxproj.add(project, 'ItemGroup', {'Label': 'ProjectConfigurations'})
        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            platform = task_gen.bld.get_platform(env.MS_PROJECT_PLATFORM)
            for variant in task_gen.bld.env.ALL_VARIANTS:
                config = self.vcxproj.add(
                    configs, 'ProjectConfiguration', {'Include': '%s-%s|%s' % (toolchain, variant, platform)}
                )
                self.vcxproj.add(config, 'Configuration', '%s-%s' % (toolchain, variant))
                self.vcxproj.add(config, 'Platform', platform)
        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            pgroup = self.vcxproj.add(project, 'PropertyGroup')
            self.vcxproj.add(pgroup, 'PlatformShortName', toolchain)
            self.vcxproj.add(pgroup, 'PlatformArchitecture', env.VALID_ARCHITECTURES[0])
            self.vcxproj.add(pgroup, 'PlatformTarget', toolchain)

        global_properties = self.vcxproj.add(project, 'PropertyGroup', {'Label': 'Globals'})
        self.vcxproj.add(global_properties, 'ProjectGUID', self.guid)
        # self.vcxproj._add(globals, 'TargetFrameworkVersion', 'v'+version_project[0])
        self.vcxproj.add(global_properties, 'RootNamespace', task_gen.target)
        self.vcxproj.add(global_properties, 'ProjectName', self.name)
        self.vcxproj.add(project, 'Import', {'Project': '$(VCTargetsPath)\\Microsoft.Cpp.Default.props'})
        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            for prop in env.MS_PROJECT_IMPORT_PROPS:
                for variant in task_gen.bld.env.ALL_VARIANTS:
                    self.vcxproj.add(
                        project, 'Import', {
                            'Condition': "'$(Configuration)'=='%s-%s'" % (toolchain, variant),
                            'Project': prop
                        }
                    )

        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = task_gen.bld.get_platform(env.MS_PROJECT_PLATFORM)
            for variant in task_gen.bld.env.ALL_VARIANTS:
                properties = self.vcxproj.add(
                    project, 'PropertyGroup',
                    {'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)}
                )
                for var in [
                    'Prefix', 'Toolchain', 'Deploy_BinDir', 'Deploy_RunBinDir', 'Deploy_LibDir', 'Deploy_IncludeDir',
                    'Deploy_DataDir', 'Deploy_PluginDir', 'Deploy_KernelDir', 'Deploy_RootDir'
                ]:
                    self.vcxproj.add(properties, var, env[var.upper()].replace('/', '\\'))
                self.vcxproj.add(properties, 'TmpDir', os.path.join(env['TMPDIR'], '..', version).replace('/', '\\'))
                self.vcxproj.add(properties, 'Variant', variant)

        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = task_gen.bld.get_platform(env.MS_PROJECT_PLATFORM)
            for variant in task_gen.bld.env.ALL_VARIANTS:
                configuration = self.vcxproj.add(
                    project, 'PropertyGroup', {
                        'Label': 'Configuration',
                        'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)
                    }
                )
                self.vcxproj.add(configuration, 'ConfigurationType', 'Makefile')
                self.vcxproj.add(configuration, 'PlatformToolset', 'v%d' % (float(version_project[1]) * 10))
                self.vcxproj.add(configuration, 'OutDir', '$(SolutionDir)$(Prefix)\\$(Variant)\\')
                self.vcxproj.add(configuration, 'IntDir', '$(TmpDir)\\$(Variant)\\')

        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = task_gen.bld.get_platform(env.MS_PROJECT_PLATFORM)
            for variant in task_gen.bld.env.ALL_VARIANTS:
                if env.MS_PROJECT_VARIABLES:
                    properties = self.vcxproj.add(
                        project, 'PropertyGroup',
                        {'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)}
                    )
                    for var, value in env.MS_PROJECT_VARIABLES:
                        self.vcxproj.add(properties, var, value)

        includes, defines = gather_includes_defines(task_gen)
        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                sub_env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            else:
                sub_env = env
            platform = task_gen.bld.get_platform(sub_env.MS_PROJECT_PLATFORM)
            for variant in task_gen.bld.env.ALL_VARIANTS:
                properties = self.vcxproj.add(
                    project, 'PropertyGroup',
                    {'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)}
                )
                command = getattr(task_gen, 'command', '')
                if command:
                    command = command % {'toolchain': toolchain, 'variant': variant}
                    self.vcxproj.add(
                        properties, 'NMakeBuildCommandLine', 'cd "$(SolutionDir)" && "%s" "%s" %s %s' %
                                                             (sys.executable, sys.argv[0], command, ' '.join(options))
                    )
                    clean_command = getattr(task_gen, 'clean_command', '')
                    if clean_command:
                        clean_command = clean_command % {'toolchain': toolchain, 'variant': variant}
                        self.vcxproj.add(
                            properties, 'NMakeCleanCommandLine', 'cd "$(SolutionDir)" && "%s" "%s" %s %s' %
                                                                 (sys.executable, sys.argv[0], clean_command,
                                                                  ' '.join(options))
                        )
                        self.vcxproj.add(
                            properties, 'NMakeReBuildCommandLine', 'cd "$(SolutionDir)" && "%s" "%s" %s %s %s' %
                                                                   (sys.executable, sys.argv[0], clean_command, command,
                                                                    ' '.join(options))
                        )
                else:
                    self.vcxproj.add(
                        properties, 'NMakeBuildCommandLine',
                        'cd "$(SolutionDir)" && "%s" "%s" build:%s:%s %s --werror --targets=%s' %
                        (sys.executable, sys.argv[0], toolchain, variant, ' '.join(options), task_gen.target)
                    )
                    self.vcxproj.add(
                        properties, 'NMakeReBuildCommandLine',
                        'cd "$(SolutionDir)" && "%s" "%s" clean:%s:%s build:%s:%s %s --werror --targets=%s' % (
                            sys.executable, sys.argv[0], toolchain, variant, ' '.join(options), toolchain, variant,
                            task_gen.target
                        )
                    )
                    self.vcxproj.add(
                        properties, 'NMakeCleanCommandLine',
                        'cd "$(SolutionDir)" && "%s" "%s" clean:%s:%s %s --targets=%s' %
                        (sys.executable, sys.argv[0], toolchain, variant, ' '.join(options), task_gen.target)
                    )
                    if 'cxxprogram' in task_gen.features:
                        self.vcxproj.add(
                            properties, 'NMakeOutput',
                            '$(OutDir)\\%s\\%s' % (env.DEPLOY_BINDIR, sub_env.cxxprogram_PATTERN % task_gen.target)
                        )
                    elif 'motor:game' in task_gen.features:
                        self.vcxproj.add(
                            properties, 'NMakeOutput', '$(OutDir)\\%s\\%s' %
                                                       (env.DEPLOY_BINDIR,
                                                        sub_env.cxxprogram_PATTERN % task_gen.bld.launcher.target)
                        )
                        self.vcxproj.add(properties, 'LocalDebuggerCommand', '$(NMakeOutput)')
                        self.vcxproj.add(properties, 'LocalDebuggerCommandArguments', task_gen.target)
                    elif 'motor:python_module' in task_gen.features:
                        self.vcxproj.add(properties, 'LocalDebuggerCommand', sys.executable)
                        self.vcxproj.add(
                            properties, 'LocalDebuggerCommandArguments',
                            '-c "import {target}; {target}.run()"'.format(target=task_gen.target)
                        )
                        self.vcxproj.add(properties, 'LocalDebuggerWorkingDirectory', '$(OutDir)')
                    self.vcxproj.add(
                        properties, 'NMakePreprocessorDefinitions',
                        ';'.join(defines + sub_env.DEFINES + sub_env.COMPILER_CXX_DEFINES)
                    )
                    if sub_env.SYS_ROOT:
                        includes.append('%s/usr/include' % sub_env.SYSROOT or '')
                    self.vcxproj.add(
                        properties, 'NMakeIncludeSearchPath', ';'.join(
                            [path_from(i, task_gen.bld.srcnode)
                             for i in includes] + sub_env.INCLUDES + sub_env.COMPILER_CXX_INCLUDES
                        )
                    )
        self.vcxproj.add(project, 'Import', {'Project': '$(VCTargetsPath)\\Microsoft.Cpp.props'})
        files = self.vcxproj.add(project, 'ItemGroup')

        for node_name, node in getattr(task_gen, 'source_nodes', []):
            self.add_node(task_gen.bld.srcnode, node, node_name, node, files)
        self.vcxproj.add(project, 'Import', {'Project': '$(VCTargetsPath)\\Microsoft.Cpp.targets'})
        for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
            env = task_gen.bld.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = task_gen.bld.get_platform(env.MS_PROJECT_PLATFORM)
            for target in env.MS_PROJECT_IMPORT_TARGETS:
                for variant in task_gen.bld.env.ALL_VARIANTS:
                    self.vcxproj.add(
                        project, 'Import', {
                            'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform),
                            'Project': target
                        }
                    )
        properties = self.vcxproj.add(project, 'PropertyGroup')
        self.vcxproj.add(properties, 'LocalDebuggerWorkingDirectory', '$(OutDir)')

    def write(self, nodes: List[waflib.Node.Node]) -> None:
        self.vcxproj.write(nodes[0])
        self.vcxfilters.write(nodes[1])

    def add_node(
            self, root_node: waflib.Node.Node, project_node: waflib.Node.Node, root_filter: str, node: waflib.Node.Node,
            files: xml.dom.minidom.Element
    ) -> None:
        path = node.abspath()
        if os.path.isdir(path):
            rel_path = node.path_from(project_node).replace('/', '\\')
            if root_filter:
                rel_path = root_filter + '\\' + rel_path
                filter_guid = generate_guid(root_filter)
                n = self.vcxfilters.add(self.filter_nodes, 'Filter', {'Include': root_filter})
                self.vcxfilters.add(n, 'UniqueIdentifier', filter_guid)

            if project_node != node:
                filter_guid = generate_guid(rel_path)
                n = self.vcxfilters.add(self.filter_nodes, 'Filter', {'Include': rel_path})
                self.vcxfilters.add(n, 'UniqueIdentifier', filter_guid)
            for subdir in node.listdir():
                self.add_node(root_node, project_node, root_filter, node.make_node(subdir), files)
        elif os.path.isfile(path):
            self.vcxproj.add(
                files, 'None', {'Include': '$(SolutionDir)%s' % node.path_from(root_node).replace('/', '\\')}
            )
            n = self.vcxfilters.add(
                self.file_nodes, 'None', {'Include': '$(SolutionDir)%s' % node.path_from(root_node).replace('/', '\\')}
            )
            if node.parent == project_node:
                rel_path = root_filter
            else:
                rel_path = node.parent.path_from(project_node).replace('/', '\\')
                if root_filter:
                    rel_path = root_filter + '\\' + rel_path
            self.vcxfilters.add(n, 'Filter', rel_path)


class VisualStudio(build_framework.ProjectGenerator):
    """creates projects for Visual Studio"""
    variant = 'vs'
    version = (('Visual Studio 15', '12.00', True, '15.0.00000.0'), (VCxproj, ('6.0', '14.1', '15.0')))
    cmd = '_vs'

    def get_platform(self, platform_name: str) -> str:
        return platform_name if platform_name in self.__class__.platforms else self.__class__.platforms[0]

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = [self.__class__.cmd]

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

    def execute(self) -> Optional[str]:
        result = build_framework.ProjectGenerator.execute(self)
        if result is not None:
            return result

        version = self.__class__.cmd
        version_name, version_number, folders, ide_version = self.__class__.version[0]
        klass, version_project = self.__class__.version[1]

        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.srcnode.name)

        solution_node = self.srcnode.make_node(appname + '.' + version + '.sln')
        projects = self.srcnode.make_node('bld').make_node(version)
        projects.mkdir()

        solution = Solution(self, version_number, version_name, folders, ide_version)

        for target, command, clean_command, do_build in [
            ('build.reconfigure', 'reconfigure', None, False), ('build.%s' % version, version, None, False),
            ('build.all', 'build:%(toolchain)s:%(variant)s', 'clean:%(toolchain)s:%(variant)s', True)
        ]:
            task_gen = self(
                target=target,
                command=command,
                clean_command=clean_command,
                all_sources=[],
                features=[],
                project_name=target
            )
            nodes = [projects.make_node("%s.%s" % (target, ext)) for ext in klass.extensions]
            project = klass(task_gen, version, version_project, folders)
            project.write(nodes)
            solution.add(task_gen, project, nodes[0].path_from(self.srcnode).replace('/', '\\'), do_build)

        for g in self.groups:
            for tg in g:
                if not isinstance(tg, waflib.TaskGen.task_gen):
                    continue
                if 'motor:kernel' in tg.features:
                    continue
                if 'motor:preprocess' in tg.features:
                    continue
                tg.post()

                nodes = [projects.make_node("%s.%s" % (tg.target, ext)) for ext in klass.extensions]
                project = klass(tg, version, version_project, folders)
                project.write(nodes)
                solution.add(tg, project, nodes[0].path_from(self.srcnode).replace('/', '\\'))

        solution.write(solution_node)
        return None


class vs2017(VisualStudio):
    """creates projects for Visual Studio 2017"""
    cmd = 'vs2017'
    variant = 'vs2017'
    version = (('Visual Studio 15', '12.00', True, '15.0.00000.0'), (VCxproj, ('6.0', '14.1', '15.0')))
    platforms = ['Win32', 'x64', 'ARM', 'Itanium']


class vs2019(VisualStudio):
    """creates projects for Visual Studio 2019"""
    cmd = 'vs2019'
    variant = 'vs2019'
    version = (('Visual Studio 16', '12.00', True, '16.0.00000.0'), (VCxproj, ('6.0', '14.2', '16.0')))
    platforms = ['Win32', 'x64', 'ARM', 'Itanium']


class vs2022(VisualStudio):
    """creates projects for Visual Studio 2022"""
    cmd = 'vs2022'
    variant = 'vs2022'
    version = (('Visual Studio 17', '12.00', True, '17.0.00000.0'), (VCxproj, ('6.0', '14.3', '17.0')))
    platforms = ['Win32', 'x64', 'ARM', 'Itanium']


class vs_cmake(build_framework.ProjectGenerator):
    """creates projects for Visual Studio using CMake"""
    cmd = 'vs-cmake'
    variant = 'vs-cmake'

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = [self.__class__.cmd]

        self.env.VARIANT = '${env .Variant}'
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

    def execute(self) -> Optional[str]:
        result = build_framework.ProjectGenerator.execute(self)
        if result is not None:
            return result

        configurations = waftools_common.cmake.write_cmake_workspace(self)
        self.write_tasks()
        self.write_launch(configurations)
        self.write_config(configurations)
        return None

    def write_tasks(self) -> None:
        tasks_file = self.path.make_node('.vs/tasks.vs.json')
        motor_tasks = [
            {
                'taskLabel': 'motor:refresh project',
                'appliesTo': '/',
                'type': 'launch',
                'command': sys.executable.replace('\\', '/'),
                'args': [sys.argv[0], self.cmd]
            },
            {
                'taskLabel': 'motor:reconfigure',
                'appliesTo': '/',
                'type': 'launch',
                'command': sys.executable.replace('\\', '/'),
                'args': [sys.argv[0], 'reconfigure']
            },
            {
                'taskLabel': 'motor:setup',
                'appliesTo': '/',
                'type': 'launch',
                'command': sys.executable.replace('\\', '/'),
                'inheritEnvironments': ['${cpp.activeConfiguration}'],
                'args': [sys.argv[0], 'setup:${env.TOOLCHAIN}:${env.BUILD_TYPE}']
            },
            {
                'taskLabel': 'motor:clean',
                'appliesTo': '/',
                'type': 'launch',
                'contextType': 'clean',
                'command': sys.executable.replace('\\', '/'),
                'inheritEnvironments': ['${cpp.activeConfiguration}'],
                'args': [sys.argv[0], 'clean:${env.TOOLCHAIN}:${env.BUILD_TYPE}']
            },
            {
                'taskLabel': 'motor:build',
                'appliesTo': '/',
                'type': 'launch',
                'contextType': 'build',
                'command': sys.executable.replace('\\', '/'),
                'inheritEnvironments': ['${cpp.activeConfiguration}'],
                'args': [sys.argv[0], 'build:${env.TOOLCHAIN}:${env.BUILD_TYPE}', '--werror']
            },
            {
                'taskLabel': 'motor:build[nomaster]',
                'appliesTo': '/',
                'type': 'launch',
                'command': sys.executable.replace('\\', '/'),
                'inheritEnvironments': ['${cpp.activeConfiguration}'],
                'args': [sys.argv[0], 'build:${env.TOOLCHAIN}:${env.BUILD_TYPE}', '--nomaster', '--werror']
            },
            {
                'taskLabel': 'motor:build[dynamic]',
                'appliesTo': '/',
                'type': 'launch',
                'command': sys.executable.replace('\\', '/'),
                'inheritEnvironments': ['${cpp.activeConfiguration}'],
                'args': [sys.argv[0], 'build:${env.TOOLCHAIN}:${env.BUILD_TYPE}', '--dynamic', '--werror']
            },
            {
                'taskLabel': 'motor:build[static]',
                'appliesTo': '/',
                'type': 'launch',
                'command': sys.executable.replace('\\', '/'),
                'inheritEnvironments': ['${cpp.activeConfiguration}'],
                'args': [sys.argv[0], 'build:${env.TOOLCHAIN}:${env.BUILD_TYPE}', '--static', '--werror']
            },
        ]
        try:
            with open(tasks_file.abspath(), 'r') as tasks_content:
                tasks = json.load(tasks_content)
            task_list = tasks['tasks']
            for motor_task in motor_tasks:
                for i, task in enumerate(task_list):
                    if task['taskLabel'] == motor_task['taskLabel']:
                        task_list[i] = motor_task
                        break
                else:
                    task_list.append(motor_task)
        except (IOError, KeyError, json.decoder.JSONDecodeError):
            tasks_file.parent.mkdir()
            tasks = {'version': '0.2', 'tasks': motor_tasks}

        with open(tasks_file.abspath(), 'w') as tasks_content:
            json.dump(tasks, tasks_content, indent=2)

    def write_launch(self, configurations: List[Tuple[str, str]]) -> None:
        assert self.launcher is not None
        targets = []
        for group in self.groups:
            for task_gen in group:
                if 'motor:game' in task_gen.features:
                    targets.append(task_gen.target)
        launch_file = self.path.make_node('.vs/launch.vs.json')
        launch_items = []
        for env_name, _ in configurations:
            env = self.all_envs[env_name]
            executable = env.cxxprogram_PATTERN % self.launcher.target
            for variant in env.ALL_VARIANTS:
                for target in targets:
                    launch_item = {
                        'project':
                            'CMakeLists.txt',
                        'projectTarget':
                            '%s (%s)' % (
                                executable,
                                os.path.join(self.path.abspath(), env.PREFIX, env.DEPLOY_BINDIR, variant,
                                             executable).replace('/', '\\')
                            ),
                        'name':
                            target,
                        'args': [target]
                    }
                    if env.LLDB:
                        launch_item['type'] = 'cppdbg'
                        launch_item['miDebuggerPath'] = env.LLDB[0]
                        launch_item['MIMode'] = 'lldb'
                        launch_item['program'] = executable
                    elif env.GDB:
                        launch_item['type'] = 'cppdbg'
                        launch_item['miDebuggerPath'] = env.GDB[0]
                        launch_item['MIMode'] = 'gdb'
                        launch_item['program'] = executable
                    else:
                        launch_item['type'] = 'default'
                    launch_items.append(launch_item)

        with open(launch_file.abspath(), 'w') as launch_content:
            json.dump({'version': '0.2.1', 'defaults': {}, 'configurations': launch_items}, launch_content, indent=2)

    def write_config(self, configurations: List[Tuple[str, str]]) -> None:
        with open('CMakePresets.json', 'w') as settings_file:
            settings_file.write('{\n'
                                '  "version": 3,\n'
                                '  "configurePresets": [\n')
            for i, (configuration, toolchain) in enumerate(configurations):
                for variant in self.env.ALL_VARIANTS:
                    last = i == len(configurations) - 1 and variant == self.env.ALL_VARIANTS[-1]
                    settings_file.write(
                        '  {\n'
                        '    "name": "%(toolchain)s-%(variant)s",\n'
                        '    "displayName": "%(toolchain)s-%(variant)s",\n'
                        '    "description": "%(toolchain)s-%(variant)s",\n'
                        '    "generator": "Ninja",\n'
                        '    "binaryDir": "%(blddir)s/%(toolchain)s/%(variant)s",\n'
                        '    "toolchainFile": "%(toolchain_file)s",\n'
                        '     "architecture": {\n'
                        '       "value": "unspecified",\n'
                        '       "strategy": "external"\n'
                        '     },\n'
                        '    "cacheVariables": {\n'
                        '      "MOTOR_TOOLCHAIN": "%(toolchain)s",\n'
                        '      "CMAKE_BUILD_TYPE": "%(variant)s",\n'
                        '      "USE_CMAKE_COMPILER_INFORMATION": true\n'
                        '    },\n'
                        '    "environment": {\n'
                        '      "TOOLCHAIN": "%(toolchain)s",\n'
                        '      "BUILD_TYPE": "%(variant)s"\n'
                        '    },\n'
                        '    "vendor": {\n'
                        '      "microsoft.com/VisualStudioSettings/CMake/1.0": {\n'
                        '        "enableClangTidyCodeAnalysis": true,\n'
                        '        "intelliSenseMode": "windows-clang-x64",\n'
                        '        "intelliSenseOptions": {\n'
                        '          "useCompilerDefaults": false\n'
                        '        }\n'
                        '      }\n'
                        '    }\n'
                        '  }%(comma_opt)s\n' % {
                            'toolchain': configuration,
                            'variant': variant,
                            'toolchain_file': toolchain.replace('\\', '/'),
                            'blddir': self.bldnode.make_node(self.variant).abspath().replace('\\', '/'),
                            'comma_opt': ',' if not last else ''
                        }
                    )
            settings_file.write('  ]\n}\n')
