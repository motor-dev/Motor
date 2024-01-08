import os
import sys
import json
import waflib.Node
import waflib.Task
import waflib.TaskGen
import xml.dom.minidom
import build_framework
from typing import Dict, IO, List, Optional, Set, Tuple, Union

_ProjectMap = Dict[str, Tuple["_ProjectMap", Optional[waflib.Task.Task]]]


def _get_platform(platform_name: str) -> str:
    platforms = ['Win32', 'x64', 'ARM', 'Itanium']
    return platform_name if platform_name in platforms else platforms[0]


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

    def write(self, file: IO[str], indent: str = '\t') -> None:
        newxml = self.document.toprettyxml(indent=indent)
        file.write(newxml)


class vcxproj(waflib.Task.Task):
    color = 'PINK'
    GUID = '{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        options = [a for a in sys.argv if a[0] == '-']
        self.m.update(repr(options).encode())
        self.m.update(str(self.env.ALL_TOOLCHAINS).encode())
        self.m.update(str(self.env.ALL_VARIANTS).encode())
        self.m.update(str(self.generator.features).encode())
        self.m.update(getattr(self, 'target_name').encode())
        self.m.update(str(getattr(self, 'include_nodes')).encode())
        self.m.update(str(getattr(self, 'defines')).encode())
        self.m.update(str(getattr(self, 'source_nodes')).encode())
        self.m.update(getattr(self, 'build_command').encode())
        self.m.update(getattr(self, 'clean_command').encode())
        self.m.update(getattr(self, 'rebuild_command').encode())

    def run(self) -> Optional[int]:
        options = [a for a in sys.argv if a[0] == '-']
        build_context = self.generator.bld
        launcher = getattr(build_context, 'launcher')  # type: waflib.TaskGen.task_gen
        target_name = getattr(self, 'target_name')  # type: str
        version_project = getattr(build_context, 'version')[1]  # type: Tuple[str, str, str]
        name = target_name.split('.')[-1]
        guid = getattr(self, 'guid')  # type: str

        vcxproj_filters = XmlFile()
        project = vcxproj_filters.add(
            vcxproj_filters.document, 'Project', {
                'DefaultTargets': 'Build',
                'ToolsVersion': version_project[2],
                'xmlns': 'http://schemas.microsoft.com/developer/msbuild/2003'
            }
        )
        filter_nodes = vcxproj_filters.add(project, 'ItemGroup')
        file_nodes = vcxproj_filters.add(project, 'ItemGroup')

        vcxproj = XmlFile()
        project = vcxproj.add(
            vcxproj.document, 'Project', {
                'DefaultTargets': 'Build',
                'ToolsVersion': version_project[2],
                'xmlns': 'http://schemas.microsoft.com/developer/msbuild/2003'
            }
        )

        def _add_node(
                root_node: waflib.Node.Node,
                project_node: waflib.Node.Node,
                root_filter: str,
                node: waflib.Node.Node,
                files: xml.dom.minidom.Element,
                seen: Set[waflib.Node.Node]
        ) -> None:
            if node not in seen:
                seen.add(node)
                if node.isdir():
                    if node != project_node:
                        _add_node(root_node, project_node, root_filter, node.parent, files, seen)

                        rel_path = node.path_from(project_node).replace('/', '\\')
                        if root_filter:
                            rel_path = root_filter + '\\' + rel_path

                        filter_guid = build_framework.generate_guid(rel_path)
                        n = vcxproj_filters.add(filter_nodes, 'Filter', {'Include': rel_path})
                        vcxproj_filters.add(n, 'UniqueIdentifier', filter_guid)
                    else:
                        if root_filter:
                            filter_guid = build_framework.generate_guid(root_filter)
                            n = vcxproj_filters.add(filter_nodes, 'Filter', {'Include': root_filter})
                            vcxproj_filters.add(n, 'UniqueIdentifier', filter_guid)
                else:
                    vcxproj.add(
                        files, 'None', {'Include': '$(SolutionDir)%s' % node.path_from(root_node).replace('/', '\\')}
                    )
                    n = vcxproj_filters.add(
                        file_nodes, 'None',
                        {'Include': '$(SolutionDir)%s' % node.path_from(root_node).replace('/', '\\')}
                    )
                    if node.parent == project_node:
                        rel_path = root_filter
                    else:
                        rel_path = node.parent.path_from(project_node).replace('/', '\\')
                        if root_filter:
                            rel_path = root_filter + '\\' + rel_path
                    vcxproj_filters.add(n, 'Filter', rel_path)

        configs = vcxproj.add(project, 'ItemGroup', {'Label': 'ProjectConfigurations'})
        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            platform = _get_platform(env.MS_PROJECT_PLATFORM)
            for variant in build_context.env.ALL_VARIANTS:
                config = vcxproj.add(
                    configs, 'ProjectConfiguration', {'Include': '%s-%s|%s' % (toolchain, variant, platform)}
                )
                vcxproj.add(config, 'Configuration', '%s-%s' % (toolchain, variant))
                vcxproj.add(config, 'Platform', platform)
        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            pgroup = vcxproj.add(project, 'PropertyGroup')
            vcxproj.add(pgroup, 'PlatformShortName', toolchain)
            vcxproj.add(pgroup, 'PlatformArchitecture', env.VALID_ARCHITECTURES[0])
            vcxproj.add(pgroup, 'PlatformTarget', toolchain)

        global_properties = vcxproj.add(project, 'PropertyGroup', {'Label': 'Globals'})
        vcxproj.add(global_properties, 'ProjectGUID', guid)
        # vcxproj._add(globals, 'TargetFrameworkVersion', 'v'+version_project[0])
        vcxproj.add(global_properties, 'RootNamespace', target_name)
        vcxproj.add(global_properties, 'ProjectName', name)
        vcxproj.add(project, 'Import', {'Project': '$(VCTargetsPath)\\Microsoft.Cpp.Default.props'})
        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            for prop in env.MS_PROJECT_IMPORT_PROPS:
                for variant in build_context.env.ALL_VARIANTS:
                    vcxproj.add(
                        project, 'Import', {
                            'Condition': "'$(Configuration)'=='%s-%s'" % (toolchain, variant),
                            'Project': prop
                        }
                    )

        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = _get_platform(env.MS_PROJECT_PLATFORM)
            for variant in build_context.env.ALL_VARIANTS:
                properties = vcxproj.add(
                    project, 'PropertyGroup',
                    {'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)}
                )
                for var in [
                    'Prefix', 'Toolchain', 'Deploy_BinDir', 'Deploy_RunBinDir', 'Deploy_LibDir', 'Deploy_IncludeDir',
                    'Deploy_DataDir', 'Deploy_PluginDir', 'Deploy_KernelDir', 'Deploy_RootDir'
                ]:
                    vcxproj.add(properties, var, env[var.upper()].replace('/', '\\'))
                tmp_dir = os.path.join(env['TMPDIR'], '..', build_context.cmd)
                vcxproj.add(properties, 'TmpDir', tmp_dir.replace('/', '\\'))
                vcxproj.add(properties, 'Variant', variant)

        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = _get_platform(env.MS_PROJECT_PLATFORM)
            for variant in build_context.env.ALL_VARIANTS:
                configuration = vcxproj.add(
                    project, 'PropertyGroup', {
                        'Label': 'Configuration',
                        'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)
                    }
                )
                vcxproj.add(configuration, 'ConfigurationType', 'Makefile')
                vcxproj.add(configuration, 'PlatformToolset', 'v%d' % (float(version_project[1]) * 10))
                vcxproj.add(configuration, 'OutDir', '$(SolutionDir)$(Prefix)\\$(Variant)\\')
                vcxproj.add(configuration, 'IntDir', '$(SolutionDir)$(Prefix)\\$(Variant)\\')

        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = _get_platform(env.MS_PROJECT_PLATFORM)
            for variant in build_context.env.ALL_VARIANTS:
                if env.MS_PROJECT_VARIABLES:
                    properties = vcxproj.add(
                        project, 'PropertyGroup',
                        {'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)}
                    )
                    for var, value in env.MS_PROJECT_VARIABLES:
                        vcxproj.add(properties, var, value)

        include_nodes = getattr(self, 'include_nodes')  # type: List[waflib.Node.Node]
        includes = [i.abspath().replace('\\', '/') for i in include_nodes]
        defines = getattr(self, 'defines')  # type: List[str]
        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                sub_env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            else:
                sub_env = env
            platform = _get_platform(sub_env.MS_PROJECT_PLATFORM)
            for variant in build_context.env.ALL_VARIANTS:
                properties = vcxproj.add(
                    project, 'PropertyGroup',
                    {'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform)}
                )
                build_command = getattr(self, 'build_command')
                build_command = build_command % {'toolchain': toolchain, 'variant': variant}
                vcxproj.add(
                    properties, 'NMakeBuildCommandLine', 'cd "$(SolutionDir)" && "%s" "%s" %s %s' %
                                                         (sys.executable, sys.argv[0], build_command, ' '.join(options))
                )

                clean_command = getattr(self, 'clean_command')
                clean_command = clean_command % {'toolchain': toolchain, 'variant': variant}
                vcxproj.add(
                    properties, 'NMakeCleanCommandLine', 'cd "$(SolutionDir)" && "%s" "%s" %s %s' %
                                                         (sys.executable, sys.argv[0], clean_command,
                                                          ' '.join(options))
                )

                rebuild_command = getattr(self, 'build_command')
                rebuild_command = rebuild_command % {'toolchain': toolchain, 'variant': variant}
                vcxproj.add(
                    properties, 'NMakeReBuildCommandLine', 'cd "$(SolutionDir)" && "%s" "%s" %s %s' %
                                                           (sys.executable, sys.argv[0], rebuild_command,
                                                            ' '.join(options))
                )

                if 'motor:vs:cxxprogram' in self.generator.features:
                    vcxproj.add(
                        properties, 'NMakeOutput',
                        '$(OutDir)\\%s\\%s' % (env.DEPLOY_BINDIR, sub_env.cxxprogram_PATTERN % target_name)
                    )
                elif 'motor:vs:game' in self.generator.features:
                    vcxproj.add(
                        properties, 'NMakeOutput', '$(OutDir)\\%s\\%s' %
                                                   (env.DEPLOY_BINDIR,
                                                    sub_env.cxxprogram_PATTERN % launcher.target)
                    )
                    vcxproj.add(properties, 'LocalDebuggerCommand', '$(NMakeOutput)')
                    vcxproj.add(properties, 'LocalDebuggerCommandArguments', target_name)
                elif 'motor:vs:python_module' in self.generator.features:
                    vcxproj.add(properties, 'LocalDebuggerCommand', sys.executable)
                    vcxproj.add(
                        properties, 'LocalDebuggerCommandArguments',
                        '-c "import {target}; {target}.run()"'.format(target=target_name)
                    )
                    vcxproj.add(properties, 'LocalDebuggerWorkingDirectory', '$(OutDir)')
                vcxproj.add(
                    properties, 'NMakePreprocessorDefinitions',
                    ';'.join(defines + sub_env.DEFINES + sub_env.COMPILER_CXX_DEFINES)
                )
                if sub_env.SYS_ROOT:
                    includes.append('%s/usr/include' % sub_env.SYSROOT or '')
                vcxproj.add(
                    properties, 'NMakeIncludeSearchPath', ';'.join(
                        includes + sub_env.INCLUDES + sub_env.COMPILER_CXX_INCLUDES
                    )
                )
        vcxproj.add(project, 'Import', {'Project': '$(VCTargetsPath)\\Microsoft.Cpp.props'})
        files = vcxproj.add(project, 'ItemGroup')

        seen = set()  # type: Set[waflib.Node.Node]
        for node_name, source_node, node_list in getattr(self, 'source_nodes'):
            for node in node_list:
                _add_node(build_context.srcnode, source_node, node_name, node, files, seen)

        vcxproj.add(project, 'Import', {'Project': '$(VCTargetsPath)\\Microsoft.Cpp.targets'})
        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            platform = _get_platform(env.MS_PROJECT_PLATFORM)
            for target in env.MS_PROJECT_IMPORT_TARGETS:
                for variant in build_context.env.ALL_VARIANTS:
                    vcxproj.add(
                        project, 'Import', {
                            'Condition': "'$(Configuration)|$(Platform)'=='%s-%s|%s'" % (toolchain, variant, platform),
                            'Project': target_name
                        }
                    )
        properties = vcxproj.add(project, 'PropertyGroup')
        vcxproj.add(properties, 'LocalDebuggerWorkingDirectory', '$(OutDir)')

        with open(self.outputs[0].abspath(), 'w') as vcxproj_file:
            vcxproj.write(vcxproj_file)
        with open(self.outputs[1].abspath(), 'w') as vcxproj_filters_file:
            vcxproj_filters.write(vcxproj_filters_file)
        return None


class vs_solution(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        def sig_project(project_map: _ProjectMap) -> None:
            for name, (subdir, task) in project_map.items():
                self.m.update(name.encode())
                if task is not None:
                    self.m.update(task.outputs[0].name.encode())
                sig_project(subdir)

        projects = getattr(self, 'projects')  # type: _ProjectMap
        sig_project(projects)

    def run(self) -> Optional[int]:
        projects = getattr(self, 'projects')  # type: _ProjectMap
        build_context = self.generator.bld
        version_name, version_number, ide_version = getattr(build_context.__class__, 'version')[0]

        def write_project(project: _ProjectMap, path: str) -> None:
            for name, (sub_projects, task) in project.items():
                if sub_projects:
                    sub_path = path + ':' + name
                    guid = build_framework.generate_guid(sub_path)
                    solution_file.write(
                        ('Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "%s", "%s", "%s"\r\n'
                         'EndProject\r\n' % (name, name, guid)
                         ).encode())
                    write_project(sub_projects, sub_path)
                if task is not None:
                    tg_guid = getattr(task, 'guid')  # type: str
                    type_guid = getattr(task, 'type_guid')  # type: str
                    project_node = task.outputs[0]
                    solution_file.write(
                        ('Project("%s") = "%s", "%s", "%s"\r\n'
                         'EndProject\r\n' % (
                             type_guid, name, project_node.path_from(build_context.srcnode),
                             tg_guid)
                         ).encode())

        def write_project_configs(project: _ProjectMap) -> None:
            for _, (sub_projects, task) in project.items():
                write_project_configs(sub_projects)
                if task is not None:
                    guid = getattr(task, 'guid')  # type: str
                    for toolchain in build_context.env.ALL_TOOLCHAINS:
                        env = build_context.all_envs[toolchain]
                        platform = _get_platform(env.MS_PROJECT_PLATFORM)
                        for variant in build_context.env.ALL_VARIANTS:
                            solution_file.write(
                                ('\t\t%s.%s|%s = %s-%s|%s\r\n' % (
                                    guid, variant, toolchain, toolchain, variant, platform)
                                 ).encode())

        def write_project_nesting(project: _ProjectMap, path: str, parent_guid: str) -> None:
            for name, (sub_projects, task) in project.items():
                if sub_projects:
                    sub_path = path + ':' + name
                    guid = build_framework.generate_guid(sub_path)
                    if parent_guid:
                        solution_file.write(('\t\t%s = %s\r\n' % (guid, parent_guid)).encode())
                    write_project_nesting(sub_projects, path, guid)
                if task is not None and parent_guid:
                    tg_guid = getattr(task, 'guid')  # type: str
                    solution_file.write(('\t\t%s = %s\r\n' % (tg_guid, parent_guid)).encode())

        with open(self.outputs[0].abspath(), 'wb') as solution_file:
            solution_file.write(
                ('\xef\xbb\xbf\r\n'
                 'Microsoft Visual Studio Solution File, Format Version %s\r\n'
                 '# %s\r\n'
                 'VisualStudioVersion = %s\r\n'
                 'MinimumVisualStudioVersion = %s\r\n'
                 '' % (version_number, version_name, ide_version, ide_version)
                 ).encode())
            write_project(projects, 'project:')
            solution_file.write(
                ('Global\r\n'
                 '\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\r\n'
                 ).encode())
            for variant in build_context.env.ALL_VARIANTS:
                for toolchain in build_context.env.ALL_TOOLCHAINS:
                    solution_file.write(('\t\t%s|%s = %s|%s\r\n' % (variant, toolchain, variant, toolchain)).encode())
            solution_file.write(
                ('\tEndGlobalSection\r\n'
                 '\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\r\n'
                 ).encode())
            write_project_configs(projects)
            solution_file.write(
                ('\tEndGlobalSection\r\n'
                 '\tGlobalSection(NestedProjects) = preSolution\r\n'
                 ).encode())
            write_project_nesting(projects, 'project:', '')
            solution_file.write(
                ('\tEndGlobalSection\r\n'
                 'EndGlobal\r\n'
                 ).encode())

        return None


class vs_tasks(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        build_context = self.generator.bld
        tasks_file = build_context.srcnode.make_node('.vs/tasks.vs.json')
        try:
            self.m.update(tasks_file.read('rb'))
        except IOError:
            pass

    def run(self) -> Optional[int]:
        build_context = self.generator.bld
        tasks_file = build_context.srcnode.make_node('.vs/tasks.vs.json')
        motor_tasks = [
            {
                'taskLabel': 'motor:refresh project',
                'appliesTo': '/',
                'type': 'launch',
                'command': sys.executable.replace('\\', '/'),
                'args': [sys.argv[0], build_context.cmd]
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

        with open(self.outputs[0].abspath(), 'w') as tasks_content:
            json.dump(tasks, tasks_content, indent=2)

        return None


class vs_launch(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        self.m.update(str(self.env.ALL_TOOLCHAINS).encode())
        self.m.update(str(self.env.ALL_VARIANTS).encode())
        self.m.update(str(getattr(self, 'targets')).encode())

    def run(self) -> Optional[int]:
        launch_items = []
        targets = getattr(self, 'targets')  # type: List[str]
        launcher = getattr(self.generator.bld, 'launcher')  # type: waflib.TaskGen.task_gen

        for toolchain in self.env.ALL_TOOLCHAINS:
            env = self.generator.bld.all_envs[toolchain]
            executable = env.cxxprogram_PATTERN % launcher.target
            for variant in self.env.ALL_VARIANTS:
                for target in targets:
                    launch_item = {
                        'project': 'CMakeLists.txt',
                        'projectTarget': '%s (%s)' % (executable,
                                                      os.path.join(self.generator.bld.path.abspath(), env.PREFIX,
                                                                   env.DEPLOY_BINDIR,
                                                                   variant,
                                                                   executable).replace('/', '\\')),
                        'name': target,
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

        with open(self.outputs[0].abspath(), 'w') as output_file:
            json.dump(
                {
                    'version': '0.2.1',
                    'defaults': {},
                    'configurations': launch_items
                },
                output_file,
                indent=2
            )

        return None


class vs_presets(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'wb') as output_file:
            pass

        return None


def make_vcxproj_task(
        solution_task_gen: waflib.TaskGen.task_gen,
        target: str,
        module_path: str,
        features: List[str],
        source_nodes: List[Tuple[str, waflib.Node.Node]],
        include_nodes: List[waflib.Node.Node],
        defines: List[str],
        build_cmd: str,
        clean_cmd: str,
        rebuild_cmd: str
) -> None:
    if 'cxxprogram' in features:
        debug_type = 'program'
    elif 'motor:game' in features:
        debug_type = 'launcher'
    elif 'motor:python_module' in features:
        debug_type = 'python'
    else:
        debug_type = ''

    all_nodes = []  # type: List[Tuple[str, waflib.Node.Node, List[waflib.Node.Node]]]
    for node_name, source_node in source_nodes:
        if source_node.isdir():
            all_nodes.append((
                node_name,
                source_node,
                source_node.ant_glob('**/*', excl=['kernels/**', 'tests/**', '**/*.pyc'], remove=False)
            ))
        else:
            all_nodes.append((node_name, source_node, [source_node]))

    vcxproj_node = build_framework.make_bld_node(solution_task_gen, None, None, target + '.vcxproj')
    vcxproj_filters_node = build_framework.make_bld_node(solution_task_gen, None, None,
                                                         target + '.vcxproj.filters')
    vcxproj_node.parent.mkdir()
    guid = build_framework.generate_guid('target:' + module_path)

    task = solution_task_gen.create_task(
        'vcxproj',
        [],
        [vcxproj_node, vcxproj_filters_node],
        target_name=target,
        defines=defines,
        include_nodes=include_nodes,
        source_nodes=all_nodes,
        build_command=build_cmd,
        clean_command=clean_cmd,
        rebuild_command=rebuild_cmd,
        guid=guid,
        debug_type=debug_type,
        type_guid=vcxproj.GUID,
        module_path=module_path,
    )

    projects = getattr(solution_task_gen, 'projects')  # type: _ProjectMap
    name = module_path.split('.')
    for c in name[:-1]:
        try:
            p_sub, _ = projects[c]
        except KeyError:
            p_sub = {}
            projects[c] = p_sub, None
        projects = p_sub
    try:
        p_sub, opt_task = projects[name[-1]]
    except KeyError:
        projects[name[-1]] = {}, task
    else:
        assert opt_task is None
        projects[name[-1]] = p_sub, task


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
@waflib.TaskGen.after_method('apply_incpaths')
def create_vcxproj_taskgen(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'visualstudio' in task_gen.bld.env.PROJECTS:
        if 'motor:makefile' in task_gen.features:
            return

        visualstudio_tg = getattr(task_gen.bld, 'visualstudio_tg')
        make_vcxproj_task(
            visualstudio_tg,
            task_gen.target,
            getattr(task_gen, 'project_name'),
            task_gen.features,
            getattr(task_gen, 'source_nodes'),
            getattr(task_gen, 'includes_nodes'),
            task_gen.env.DEFINES,
            'build:%(toolchain)s:%(variant)s --werror --targets=' + task_gen.target,
            'clean:%(toolchain)s:%(variant)s --targets=' + task_gen.target,
            'clean:%(toolchain)s:%(variant)s build:%(toolchain)s:%(variant)s --werror --targets=' + task_gen.target
        )


@waflib.TaskGen.feature('motor:makefile')
@waflib.TaskGen.after_method('apply_incpaths')
def create_mak_taskgen(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'visualstudio' in task_gen.bld.env.PROJECTS:
        visualstudio_tg = getattr(task_gen.bld, 'visualstudio_tg')

        make_vcxproj_task(
            visualstudio_tg,
            task_gen.target,
            getattr(task_gen, 'project_name'),
            task_gen.features,
            getattr(task_gen, 'source_nodes'),
            getattr(task_gen, 'includes_nodes'),
            task_gen.env.DEFINES,
            'build:%(toolchain)s:%(variant)s --werror',
            'clean:%(toolchain)s:%(variant)s',
            'clean:%(toolchain)s:%(variant)s build:%(toolchain)s:%(variant)s --werror',
        )

        make_vcxproj_task(
            visualstudio_tg,
            'reconfigure',
            'reconfigure',
            [],
            [],
            [],
            [],
            'reconfigure',
            '',
            'reconfigure',
        )

        make_vcxproj_task(
            visualstudio_tg,
            'setup',
            'setup',
            [],
            [],
            [],
            [],
            'setup:%(toolchain)s:%(variant)s',
            '',
            'setup:%(toolchain)s:%(variant)s',
        )

        make_vcxproj_task(
            visualstudio_tg,
            'refresh_projects',
            'refresh_projects',
            [],
            [],
            [],
            [],
            'task_gen.bld.cmd',
            '',
            'task_gen.bld.cmd',
        )


@waflib.TaskGen.feature('motor:vs:solution')
def create_solution(task_gen: waflib.TaskGen.task_gen) -> None:
    appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, task_gen.bld.srcnode.name)
    projects = getattr(task_gen, 'projects')  # type: _ProjectMap
    solution_file = build_framework.make_bld_node(task_gen, None, None, appname + '.%s.sln' % task_gen.bld.cmd)
    solution_file.parent.mkdir()
    task_gen.create_task('vs_solution', [], [solution_file], projects=projects)
    build_framework.install_files(task_gen, task_gen.bld.srcnode.abspath(), [solution_file])


@waflib.TaskGen.feature('motor:vs:cmake')
def create_vs_cmake_project(task_gen: waflib.TaskGen.task_gen) -> None:
    vs_node = task_gen.bld.srcnode.make_node('.vs')
    tasks_node = build_framework.make_bld_node(task_gen, None, None, 'tasks.vs.json')
    launch_node = build_framework.make_bld_node(task_gen, None, None, 'launch.vs.json')
    presets_node = build_framework.make_bld_node(task_gen, None, None, 'CMakePresets.json')
    tasks_node.parent.mkdir()

    targets = []
    for group in task_gen.bld.groups:
        for tg in group:
            if 'motor:game' in tg.features:
                targets.append(tg.target)

    task_gen.create_task('vs_tasks', [], [tasks_node])
    task_gen.create_task('vs_launch', [], [launch_node], targets=targets)
    task_gen.create_task('vs_presets', [], [presets_node])

    build_framework.install_files(task_gen, vs_node.abspath(), [tasks_node, launch_node])
    # build_framework.install_files(task_gen, task_gen.bld.srcnode.abspath(), [presets_node])


def build(build_context: build_framework.BuildContext) -> None:
    if 'visualstudio' in build_context.env.PROJECTS:
        visualstudio_tg = build_context(
            group=build_context.cmd,
            target='projects',
            features=['motor:vs:solution'],
            projects={}
        )
        setattr(build_context, 'visualstudio_tg', visualstudio_tg)
    if 'vs-cmake' in build_context.env.PROJECTS:
        build_context(
            group=build_context.cmd,
            target='vs-cmake',
            features=['motor:vs:cmake'],
        )
