import json
import json_minify
import os
import sys
import shutil
import build_framework
import waflib.ConfigSet
import waflib.Node
import waflib.TaskGen
import waflib.Utils
from typing import Dict, List, Optional, Union


def _get_define(define: str) -> str:
    index = define.find('=')
    if index == -1:
        return '#define %s' % define
    else:
        return '#define %s %s' % (define[:index], define[index + 1:])


def _get_intellisense_mode(env: waflib.ConfigSet.ConfigSet) -> str:
    if 'darwin' in env.VALID_PLATFORMS:
        platform = 'macos'
    elif 'windows' in env.VALID_PLATFORMS:
        platform = 'windows'
    else:
        platform = 'linux'

    if 'arm64' in env.VALID_ARCHITECTURES:
        arch = 'arm64'
    elif 'arm' == env.ARCH_FAMILY:
        arch = 'arm'
    elif 'x86' in env.VALID_ARCHITECTURES:
        arch = 'x86'
    else:
        arch = 'x64'

    if env.COMPILER_NAME == 'gcc':
        compiler = 'gcc'
    elif env.COMPILER_NAME == 'msvc':
        compiler = 'msvc'
    else:
        compiler = 'clang'

    return '%s-%s-%s' % (platform, compiler, arch)


@build_framework.autosig_vars('extensions')
class vscode_workspace(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)

        with open(self.outputs[0].abspath(), 'w') as workspace:
            workspace.write(
                '{\n'
                '  "folders": [\n'
                '    {\n'
                '      "path": ".",\n'
                '      "name": "%s"\n'
                '    }\n'
                '  ],\n'
                '  "extensions": {\n'
                '    "recommendations": [\n'
                '      %s\n'
                '    ]\n'
                '  }\n'
                '}\n' % (appname, ',\n      '.join(getattr(self, 'extensions')))
            )
        return None


class vscode_settings(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as settings:
            settings.write(
                '  {\n'
                '    "editor.formatOnSave": true,\n'
                '    "editor.formatOnType": true,\n'
                '    "python.autoComplete.extraPaths": [\n'
                '      "%(motorpath)s/mak/lib",\n'
                '      "%(motorpath)s/mak/typeshed",\n'
                '      "%(motorpath)s/mak/vendor"\n'
                '    ],\n'
                '    "python.analysis.extraPaths": [\n'
                '      "%(motorpath)s/mak/lib",\n'
                '      "%(motorpath)s/mak/typeshed",\n'
                '      "%(motorpath)s/mak/vendor"\n'
                '    ],\n'
                '    "files.exclude": {\n'
                '      "**/.git": true,\n'
                '      "**/.svn": true,\n'
                '      "**/.hg": true,\n'
                '      "**/CVS": true,\n'
                '      "**/.DS_Store": true,\n'
                '      "**/__pycache__": true,\n'
                '      "**/*.pyc": true,\n'
                '      "bld/.waf/*-*-*": true,\n'
                '      "bld/.waf/*.*": true,\n'
                '      "**/.clangd": true,\n'
                '      "**/.mypy_cache": true,\n'
                '    },\n'
                '    "files.watcherExclude": {\n'
                '      "**/.git/*": true,\n'
                '      "**/bld/**": true\n'
                '    },\n'
                '    "clangd.arguments": [\n'
                '      "--header-insertion=never"\n'
                '    ],\n'
                '    "C_Cpp.codeAnalysis.clangTidy.enabled": true,\n'
                '    "C_Cpp.codeAnalysis.clangTidy.useBuildPath": true,\n'
                '    "cmake.buildDirectory": "${workspaceFolder}/%(projectpath)s/vscode.bld/${buildKit}/${buildType}",\n'
                '    "cmake.showSystemKits": false,\n'
                '    "[python]": {\n'
                '        "editor.defaultFormatter": "eeyore.yapf",\n'
                '        "editor.formatOnSave": true\n'
                '    }\n'
                '  }\n' % {
                    'motorpath': getattr(self.generator.bld, 'motornode').path_from(self.generator.bld.srcnode),
                    'projectpath': self.generator.bld.bldnode.path_from(self.generator.bld.srcnode)
                }
            )
        return None


class vscode_properties(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)

    def run(self) -> Optional[int]:
        configurations = []
        for toolchain in self.env.ALL_TOOLCHAINS:
            bld_env = self.generator.bld.all_envs[toolchain]
            if bld_env.SUB_TOOLCHAINS:
                env = self.generator.bld.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env
            properties = {}
            for var in [
                'Prefix', 'TmpDir', 'Toolchain', 'Deploy_BinDir', 'Deploy_RunBinDir', 'Deploy_LibDir',
                'Deploy_IncludeDir', 'Deploy_DataDir', 'Deploy_PluginDir', 'Deploy_KernelDir', 'Deploy_RootDir'
            ]:
                properties[var] = bld_env[var.upper()]
            properties['Launcher'] = env.cxxprogram_PATTERN % getattr(self.generator.bld, 'launcher').target
            properties['Python'] = sys.executable
            if env.GDB:
                properties['DebuggerType'] = 'cppdbg'
                properties['DebuggerMode'] = 'gdb'
                properties['DebuggerPath'] = env.GDB[0]
            elif env.CDB:
                properties['DebuggerType'] = 'cppvsdbg'
            elif env.LLDB:
                properties['DebuggerType'] = 'cppdbg'
                properties['DebuggerMode'] = 'lldb'
                properties['DebuggerPath'] = env.LLDB[0]
            else:
                properties['DebuggerType'] = 'cppdbg'
                properties['DebuggerMode'] = 'gdb'
                properties['DebuggerPath'] = '/usr/bin/gdb'

            for variant in self.env.ALL_VARIANTS:
                properties['Variant'] = variant
                compile_commands = build_framework.make_bld_node(
                    self.generator, 'compile_commands', toolchain, 'compile_commands.json'
                )
                configurations.append(
                    {
                        'name':
                            '%s - %s' % (toolchain, variant),
                        'compileCommands':
                            '${workspaceFolder}/%s' % compile_commands.path_from(self.generator.bld.srcnode),
                        'customConfigurationVariables':
                            properties,
                        'intelliSenseMode': _get_intellisense_mode(env),
                        'compilerPath': ''
                    }
                )
        with open(self.outputs[0].abspath(), 'w') as property_file:
            json.dump({'configurations': configurations}, property_file, indent=2)
        return None


class vscode_tasks(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        options = [a for a in sys.argv if a[0] == '-']
        tasks_file = self.generator.bld.srcnode.make_node('.vscode/tasks.json')
        try:
            tasks = json.loads(json_minify.json_minify(waflib.Utils.readf(tasks_file.abspath(), 'r')))
        except (IOError, json.JSONDecodeError):
            tasks = {'version': '2.0.0', 'tasks': [], 'inputs': []}
        else:
            tasks['tasks'] = [t for t in tasks['tasks'] if not t['label'].startswith('motor:')]
            try:
                tasks['inputs'] = [i for i in tasks['inputs'] if not i['id'].startswith('motor-')]
            except KeyError:
                tasks['inputs'] = []

        for action, command, is_default in [
            (
                    'build',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '-p', '--werror'],
                    True
            ),
            (
                    'build[fail-tests=no]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--no-fail-on-tests', '-p', '--werror'],
                    False
            ),
            (
                    'build[static]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--static', '-p', '--werror'],
                    False
            ),
            (
                    'build[dynamic]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--dynamic', '-p', '--werror'],
                    False
            ),
            (
                    'build[nomaster]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--nomaster', '-p', '--werror'],
                    False
            ),
            (
                    'build[single]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '-j', '1', '-p', '--werror'],
                    False
            ),
            (
                    'clean',
                    ['clean:${input:motor-Toolchain}:${input:motor-Variant}', '-p'],
                    False
            ),
            (
                    'rebuild',
                    ['clean:${input:motor-Toolchain}:${input:motor-Variant}',
                     'build:${input:motor-Toolchain}:${input:motor-Variant}', '-p', '--werror'],
                    False
            ),
            (
                    'setup',
                    ['setup:${input:motor-Toolchain}'],
                    False
            ),
            (
                    'reconfigure',
                    ['reconfigure'],
                    False
            ),
            (
                    self.generator.bld.cmd,
                    [self.generator.bld.cmd],
                    False
            )
        ]:
            tasks['tasks'].append(
                {
                    'label': 'motor:%s' % action,
                    'type': 'process',
                    'command': [sys.executable],
                    'args': [sys.argv[0]] + command + options,
                    'options': {
                        'cwd': self.generator.bld.srcnode.abspath()
                    },
                    'problemMatcher': ['$gcc', '$msCompile'],
                    'group': {
                        'kind': 'build',
                        'isDefault': True
                    } if is_default else 'build'
                }
            )

        tasks['tasks'].append(
            {
                'label': 'motor:mypy',
                'type': 'process',
                'command': [sys.executable],
                'args': ['-m', 'mypy', '--show-column-numbers'],
                'options': {
                    'cwd': self.generator.bld.srcnode.abspath()
                },
                'problemMatcher': ['$gcc', '$msCompile'],
                'group': 'build'
            }
        )

        for input_variable in ('Toolchain', 'Variant'):
            tasks['inputs'].append(
                {
                    'id': 'motor-%s' % input_variable,
                    'type': 'command',
                    'command': 'cpptools.activeConfigCustomVariable',
                    'args': input_variable
                }
            )

        with open(self.outputs[0].abspath(), 'w') as document:
            json.dump(tasks, document, indent=2)

        return None


class vscode_launch(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        for tg in getattr(self, 'launch_tasks'):
            self.m.update(tg.target.encode())

    def run(self) -> Optional[int]:
        options = [a for a in sys.argv if a[0] == '-']
        launch_file = self.generator.bld.srcnode.make_node('.vscode/launch.json')
        try:
            launch_config_content = json_minify.json_minify(waflib.Utils.readf(launch_file.abspath(), 'r'))
            launch_configs = json.loads(launch_config_content)
        except (IOError, json.JSONDecodeError):
            launch_configs = {'version': '0.2.0', 'configurations': [], 'inputs': []}
        else:
            launch_configs['configurations'] = [
                c for c in launch_configs['configurations'] if not c['name'].startswith('motor:')
            ]
            try:
                launch_configs['inputs'] = [i for i in launch_configs['inputs'] if not i['id'].startswith('motor-')]
            except KeyError:
                launch_configs['inputs'] = []

        for action, command in [
            (
                    'build',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '-p', '--werror']
            ),
            (
                    'build[fail-tests=no]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--no-fail-on-tests', '-p', '--werror']
            ),
            (
                    'build[static]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--static', '-p', '--werror']
            ),
            (
                    'build[dynamic]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--dynamic', '-p', '--werror']
            ),
            (
                    'build[nomaster]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--nomaster', '-p', '--werror']
            ),
            (
                    'build[single]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '-j', '1', '-p', '--werror']
            ),
            (
                    'clean',
                    ['clean:${input:motor-Toolchain}:${input:motor-Variant}', '-p']
            ),
            (
                    'rebuild', [
                        'clean:${input:motor-Toolchain}:${input:motor-Variant}',
                        'build:${input:motor-Toolchain}:${input:motor-Variant}', '-p', '--werror'
                    ]
            ),
            (
                    'setup',
                    ['setup:${input:motor-Toolchain}']
            ),
            (
                    'reconfigure',
                    ['reconfigure']
            ),
            (
                    self.generator.bld.cmd,
                    [self.generator.bld.cmd]
            )
        ]:
            launch_configs['configurations'].append(
                {
                    'name': 'motor:waf:%s' % action,
                    'type': 'python',
                    'request': 'launch',
                    'program': sys.argv[0],
                    'args': command + options,
                    'cwd': '${workspaceFolder}',
                    'env': {
                        'PYDEVD_DISABLE_FILE_VALIDATION': '1'
                    }
                }
            )

        for tg in getattr(self, 'launch_tasks'):
            if 'motor:game' in tg.features:
                launch_configs['configurations'].append(
                    {
                        'name': 'motor:%s' % tg.target,
                        'type': 'cppdbg',
                        'request': 'launch',
                        'program':
                            '${workspaceFolder}/${input:motor-Prefix}/${input:motor-Variant}/'
                            '${input:motor-Deploy_BinDir}/${input:motor-Launcher}',
                        'args': [tg.target],
                        'cwd': '${workspaceFolder}',
                        'miDebuggerPath': '${input:motor-DebuggerPath}',
                        'MIMode': '${input:motor-DebuggerMode}',
                        'windows': {
                            'type': 'cppvsdbg'
                        },
                        'preLaunchTask': 'motor:build'
                    }
                )
            if 'motor:python_module' in tg.features:
                launch_configs['configurations'].append(
                    {
                        'name': 'motor:%s' % tg.target,
                        'type': 'cppdbg',
                        'request': 'launch',
                        'program': '${input:motor-Python}',
                        'miDebuggerPath': '${input:motor-DebuggerPath}',
                        'MIMode': '${input:motor-DebuggerMode}',
                        'args': ['-c', 'import py_motor; py_motor.run()'],
                        'cwd':
                            '${workspaceFolder}/${input:motor-Prefix}/${input:motor-Variant}/'
                            '${input:motor-Deploy_RunBinDir}',
                        'windows': {
                            'type': 'cppvsdbg'
                        },
                        'preLaunchTask': 'motor:build'
                    }
                )
            if 'motor:unit_test' in tg.features:
                link_task = getattr(tg, 'link_task')  # type: waflib.Task.Task
                unit_test = link_task.outputs[0].path_from(tg.bld.bldnode)
                launch_configs['configurations'].append(
                    {
                        'name': 'motor:%s' % tg.target,
                        'type': 'cppdbg',
                        'request': 'launch',
                        'program': '${input:motor-TmpDir}/${input:motor-Variant}/%s' % unit_test,
                        'miDebuggerPath': '${input:motor-DebuggerPath}',
                        'MIMode': '${input:motor-DebuggerMode}',
                        'args': [],
                        'cwd': '${input:motor-TmpDir}/${input:motor-Variant}',
                        'windows': {
                            'type': 'cppvsdbg'
                        },
                        'preLaunchTask': 'motor:build[fail-tests=no]'
                    }
                )

        for input_variable in (
                'Toolchain', 'Variant', 'Prefix', 'Deploy_RunBinDir', 'Deploy_BinDir', 'Launcher', 'Python',
                'DebuggerPath',
                'DebuggerMode', 'TmpDir'
        ):
            launch_configs['inputs'].append(
                {
                    'id': 'motor-%s' % input_variable,
                    'type': 'command',
                    'command': 'cpptools.activeConfigCustomVariable',
                    'args': input_variable
                }
            )

        with open(self.outputs[0].abspath(), 'w') as document:
            json.dump(launch_configs, document, indent=2)
        return None


class vscode_cmake_launch(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        for tg in getattr(self, 'launch_tasks'):
            self.m.update(tg.target.encode())

    def run(self) -> Optional[int]:
        options = [a for a in sys.argv if a[0] == '-']
        launch_file = self.generator.bld.srcnode.make_node('.vscode/launch.json')
        try:
            launch_config_content = json_minify.json_minify(waflib.Utils.readf(launch_file.abspath(), 'r'))
            launch_configs = json.loads(launch_config_content)
        except (IOError, json.JSONDecodeError):
            launch_configs = {'version': '0.2.0', 'configurations': [], 'inputs': []}
        else:
            launch_configs['configurations'] = [
                c for c in launch_configs['configurations'] if not c['name'].startswith('motor:')
            ]

        for action, command in [
            (
                    'build',
                    ['build:${buildKit}:${buildType}', '-p', '--werror']
            ),
            (
                    'build[fail-tests=no]',
                    ['build:${buildKit}:${buildType}', '--no-fail-on-tests', '-p', '--werror']
            ),
            (
                    'build[static]',
                    ['build:${buildKit}:${buildType}', '--static', '-p', '--werror']
            ),
            (
                    'build[dynamic]',
                    ['build:${buildKit}:${buildType}', '--dynamic', '-p', '--werror']
            ),
            (
                    'build[nomaster]',
                    ['build:${buildKit}:${buildType}', '--nomaster', '-p', '--werror']
            ),
            (
                    'build[single]',
                    ['build:${buildKit}:${buildType}', '-j', '1', '-p', '--werror']
            ),
            (
                    'clean',
                    ['clean:${buildKit}:${buildType}', '-p']
            ),
            (
                    'rebuild', [
                        'clean:${buildKit}:${buildType}',
                        'build:${buildKit}:${buildType}', '-p', '--werror'
                    ]
            ),
            (
                    'setup',
                    ['setup:${buildKit}']
            ),
            (
                    'reconfigure',
                    ['reconfigure']
            ),
            (
                    self.generator.bld.cmd,
                    [self.generator.bld.cmd]
            )
        ]:
            launch_configs['configurations'].append(
                {
                    'name': 'motor:waf:%s' % action,
                    'type': 'python',
                    'request': 'launch',
                    'program': sys.argv[0],
                    'args': command + options,
                    'cwd': '${workspaceFolder}',
                    'env': {
                        'PYDEVD_DISABLE_FILE_VALIDATION': '1'
                    }
                }
            )

        debuggers = set()
        for env_name in self.env.ALL_TOOLCHAINS:
            bld_env = self.generator.bld.all_envs[env_name]
            if bld_env.GDB:
                debuggers.add(('gdb', 'cppdbg', 'gdb'))
            if bld_env.LLDB:
                debuggers.add(('lldb', 'cppdbg', 'lldb'))
            if bld_env.CDB:
                debuggers.add(('cdb', 'cppvsdbg', ''))

        for tg in getattr(self, 'launch_tasks'):
            if 'motor:game' in tg.features:
                for name, category, _ in debuggers:
                    launch_configs['configurations'].append(
                        {
                            'name': 'motor:%s[%s]' % (tg.target, name),
                            'type': category,
                            'request': 'launch',
                            'program': '${command:cmake.launchTargetPath}',
                            'args': [tg.target],
                            'cwd': '${workspaceFolder}',
                        }
                    )

        with open(self.outputs[0].abspath(), 'w') as document:
            json.dump(launch_configs, document, indent=2)
        return None


class vscode_commands(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        for task in getattr(self, 'files'):
            self.m.update(str(task.inputs[0]).encode())
        for c_file in getattr(self, 'compiler_files'):
            self.m.update(str(c_file).encode())

    def run(self) -> Optional[int]:
        files = getattr(self, 'files')  # type: List[waflib.Task.Task]
        compiler_file_c, compiler_file_cxx, compiler_exe_c, compiler_exe_cxx = getattr(self, 'compiler_files')
        env = getattr(self, 'bld_env')
        commands = []  # type: List[Dict[str, Union[str, List[str]]]]
        target = ['-target', env.COMPILER_TARGET]

        for task in files:
            input = task.inputs[0]
            if input.is_child_of(self.generator.bld.bldnode):
                continue
            if build_framework.apply_source_filter(task.generator, env, input)[0]:
                if task.__class__.__name__ in ('c', 'objc'):
                    compiler = [compiler_exe_c.abspath(), '-nostdinc', '-x', 'c', '-c',
                                '@%s' % compiler_file_c.abspath()] + target
                else:
                    compiler = [compiler_exe_cxx.abspath(), '-nostdinc', '-x', 'c++', '-c',
                                '-std=c++14',
                                '@%s' % compiler_file_cxx.abspath()] + target
                if env.SYSROOT:
                    compiler = compiler + ['-isysroot"%s"' % env.SYSROOT]
                tgen_response = build_framework.make_bld_node(
                    self.generator, 'response_files', '', task.generator.target + '.txt'
                ).path_from(self.generator.bld.srcnode)
                commands.append(
                    {
                        'directory': self.generator.bld.srcnode.abspath(),
                        'command': ' '.join(compiler + ['@%s' % tgen_response, input.abspath()]),
                        'file': task.inputs[0].path_from(self.generator.bld.srcnode),
                        'output': task.outputs[0].path_from(self.generator.bld.srcnode),
                    }
                )
        with open(self.outputs[0].abspath(), 'w') as compile_commands_file:
            json.dump(commands, compile_commands_file, indent=2)
        return None


@build_framework.autosig_vars('include_nodes', 'include_paths', 'defines')
class vscode_response(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as response_file:
            for include in getattr(self, 'include_nodes'):
                response_file.write('-I"%s"\n' % include.abspath())
            for include in getattr(self, 'include_paths'):
                response_file.write('-isystem"%s"\n' % include)
            for define in getattr(self, 'defines'):
                response_file.write('-D"%s"\n' % define.replace('"', '\\"'))
        return None


@build_framework.autosig_vars('target', 'include_paths', 'defines', 'platforms')
class vscode_compiler(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        motor_node = getattr(self.generator.bld, 'motornode')  # type: waflib.Node.Node
        include_path = motor_node.make_node('mak/compiler/vscode')
        extra_includes = []
        for platform in getattr(self, 'platforms'):
            include_path = include_path.make_node(platform)
            if include_path.isdir():
                extra_includes.append(include_path.abspath())
        with open(self.outputs[0].abspath(), 'w') as compiler_file:
            compiler_file.write(
                '--target=%(target)s\n'
                '%(includes)s\n'
                '%(defines)s\n'
                '-D__builtin_ia32_addss(_1,_2)=_1\n'
                '-D__builtin_ia32_addsd(_1,_2)=_1\n'
                '-D__builtin_ia32_subss(_1,_2)=_1\n'
                '-D__builtin_ia32_subsd(_1,_2)=_1\n'
                '-D__builtin_ia32_mulss(_1,_2)=_1\n'
                '-D__builtin_ia32_mulsd(_1,_2)=_1\n'
                '-D__builtin_ia32_divss(_1,_2)=_1\n'
                '-D__builtin_ia32_divsd(_1,_2)=_1\n'
                '-D__builtin_ia32_andps(_1,_2)=_1\n'
                '-D__builtin_ia32_andpd(_1,_2)=_1\n'
                '-D__builtin_ia32_andnps(_1,_2)=_1\n'
                '-D__builtin_ia32_andnpd(_1,_2)=_1\n'
                '-D__builtin_ia32_orps(_1,_2)=_1\n'
                '-D__builtin_ia32_orpd(_1,_2)=_1\n'
                '-D__builtin_ia32_xorps(_1,_2)=_1\n'
                '-D__builtin_ia32_xorpd(_1,_2)=_1\n'
                '-D__builtin_ia32_movss(_1,_2)=_1\n'
                '-D__builtin_ia32_movsd(_1,_2)=_1\n'
                '-D__builtin_ia32_movq128(_1)=_1\n'
                '-D__builtin_ia32_cmpgtps(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpgtpd(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpgeps(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpgepd(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpleps(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpngtps(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpngtpd(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpnltps(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpngeps(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpngepd(_1,_2)=_1\n'
                '-D__builtin_ia32_cmpnleps(_1,_2)=_1\n'
                '-D__builtin_ia32_cvtsi2ss(_1,_2)=_1\n'
                '-D__builtin_ia32_cvtsd2ss(_1,_2)=_1\n'
                '-D__builtin_ia32_cvtsi2ss(_1,_2)=_1\n'
                '-D__builtin_ia32_cvtdq2ps(_1)=_1\n'
                '-D__builtin_ia32_cvtdq2pd(_1)=_1\n'
                '-D__builtin_ia32_cvtdq2ps(_1)=_1\n'
                '-D__builtin_ia32_cvtsi2sd(_1,_2)=_1\n'
                '-D__builtin_ia32_cvtss2sd(_1,_2)=_1\n'
                '-D__builtin_ia32_cvtps2pd(_1)=_1\n'
                '-D__builtin_ia32_movlhps(_1,_2)=_1\n'
                '-D__builtin_ia32_movhlps(_1,_2)=_1\n'
                '-D__builtin_ia32_unpckhps(_1,_2)=_1\n'
                '-D__builtin_ia32_unpckhpd(_1,_2)=_1\n'
                '-D__builtin_ia32_unpcklps(_1,_2)=_1\n'
                '-D__builtin_ia32_unpcklpd(_1,_2)=_1\n'
                '-D__builtin_ia32_punpckhbw128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpckhwd128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpckhdq128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpckqdq128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpcklbw128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpcklwd128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpckldq128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpckhqdq128(_1,_2)=_1\n'
                '-D__builtin_ia32_punpcklqdq128(_1,_2)=_1\n'
                '-D__builtin_ia32_paddsb128(_1,_2)=_1\n'
                '-D__builtin_ia32_paddsw128(_1,_2)=_1\n'
                '-D__builtin_ia32_paddusb128(_1,_2)=_1\n'
                '-D__builtin_ia32_paddusw128(_1,_2)=_1\n'
                '-D__builtin_ia32_psubsb128(_1,_2)=_1\n'
                '-D__builtin_ia32_psubsw128(_1,_2)=_1\n'
                '-D__builtin_ia32_psubusb128(_1,_2)=_1\n'
                '-D__builtin_ia32_psubusw128(_1,_2)=_1\n'
                '-D__builtin_ia32_pandn128(_1,_2)=_1\n'
                '-D__builtin_ia32_pmaxsw128(_1,_2)=_1\n'
                '-D__builtin_ia32_pmaxub128(_1,_2)=_1\n'
                '-D__builtin_ia32_pminsw128(_1,_2)=_1\n'
                '-D__builtin_ia32_pminub128(_1,_2)=_1\n'
                '-D__builtin_ia32_loadhps(_1,_2)=_1\n'
                '-D__builtin_ia32_movntps(_1,_2)=_1\n'
                '-D__builtin_ia32_loadhps(_1,_2)=_1\n'
                '-D__builtin_ia32_loadlps(_1,_2)=_1\n'
                '-D__builtin_ia32_loadhpd(_1,_2)=_1\n'
                '-D__builtin_ia32_loadlpd(_1,_2)=_1\n'
                '-D__builtin_ia32_storehps(_1,_2)=\n'
                '-D__builtin_ia32_storelps(_1,_2)=\n'
                '-D__builtin_ia32_movntq(_1,_2)=\n'
                '-D__builtin_ia32_movntdq(_1,_2)=\n'
                '-D__builtin_ia32_movntpd(_1,_2)=\n'
                '-D__builtin_shuffle(_1...)=_1\n'
                '-D_mm_getcsr=_mm_getcsr_redirect\n'
                '-D_mm_setcsr=_mm_setcsr_redirect\n'
                '-D_mm_sfence=_mm_sfense_redirect\n'
                '-D_mm_lfence=_mm_lfense_redirect\n'
                '-D_mm_mfence=_mm_mfense_redirect\n'
                '-D_mm_pause=_mm_pause_redirect\n'
                '-D_mm_clflush=_mm_clflush_redirect\n'
                '-D__malloc__(dealloc,argno)=__malloc__\n'
                '' % {
                    'target': getattr(self, 'target'),
                    'includes': '\n'.join(
                        ['-isystem"%s"' % i for i in getattr(self, 'include_paths') + extra_includes]),
                    'defines': '\n'.join(['-D"%s"' % d.replace('"', '\\"') for d in getattr(self, 'defines')])
                }
            )
        with open(self.outputs[1].abspath(), 'w') as compiler_shell:
            compiler_shell.write(
                '#! /bin/sh\n'
                '%s %s "$@"\n'
                '' % (sys.executable, self.outputs[3].abspath())
            )
        os.chmod(self.outputs[1].abspath(), 0o755)
        with open(self.outputs[2].abspath(), 'w') as compiler_bat:
            compiler_bat.write(
                '%s %s %%*"\n'
                '' % (sys.executable, self.outputs[3].abspath())
            )

        with open(self.outputs[3].abspath(), 'w') as compiler_py:
            compiler_py.write(
                'import sys\n'
                'if "-dumpmachine" in sys.argv:\n'
                '    print("%(target)s")\n'
                'else:\n'
                '    print("""clang -cc1 version 16.0.6 based upon LLVM 16.0.6 default target %(target)s\n'
                '#include "..." search starts here:\n'
                '#include <...> search starts here:\n'
                ' %(includes)s\n'
                'End of search list.\n'
                '%(defines)s\n'
                '""")\n' % {
                    'target': getattr(self, 'target'),
                    'includes': '\n '.join(getattr(self, 'include_paths')),
                    'defines': '\n'.join([_get_define(d) for d in getattr(self, 'defines')])
                }
            )

        return None


@build_framework.autosig_vars('toolchains')
class vscode_kits(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        kits = [{'name': toolchain, 'toolchainFile': toolchain_file,
                 'cmakeSettings': {'USE_CMAKE_COMPILER_INFORMATION': '1'}} for
                toolchain, toolchain_file in
                getattr(self, 'toolchains')]
        with open(self.outputs[0].abspath(), 'w') as kits_file:
            json.dump(kits, kits_file, indent=2)


@build_framework.autosig_vars('variants')
class vscode_variants(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        variant_names = getattr(self, 'variants')  # type: List[str]
        variants = {
            'buildTypes': {
                'default': variant_names[0],
                'description': 'build types',
                'choices': {
                    name: {
                        'short': name,
                        'long': 'build %s' % name,
                        'buildType': name
                    } for name in variant_names
                }
            }
        }
        with open(self.outputs[0].abspath(), 'w') as variants_file:
            json.dump(variants, variants_file, indent=2)


@waflib.TaskGen.feature('motor:vscode', 'motor:vscode:cmake')
def vscode_make_workspace(task_gen: waflib.TaskGen.task_gen) -> None:
    appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, task_gen.bld.srcnode.name)
    settings_node = build_framework.make_bld_node(task_gen, None, None, 'settings.json')
    settings_node.parent.mkdir()
    task_gen.create_task('vscode_settings', [], [settings_node])
    build_framework.install_files(task_gen, os.path.join(task_gen.bld.srcnode.abspath(), '.vscode'),
                                  [settings_node])
    workspace_node = build_framework.make_bld_node(task_gen, None, None, '%s.code-workspace' % appname)
    task_gen.create_task('vscode_workspace', [], [workspace_node], extensions=getattr(task_gen.bld, 'extensions'))
    build_framework.install_files(task_gen, task_gen.bld.srcnode.abspath(), [workspace_node])


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
@waflib.TaskGen.after_method('apply_incpaths')
def vscode_make_response_file(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'vscode' in task_gen.bld.env.PROJECTS:
        vscode = getattr(task_gen.bld, 'vscode')
        files = getattr(vscode, 'files')  # type: List[waflib.Task.Task]
        for task in task_gen.tasks:
            if task.__class__.__name__ in ('c', 'objc', 'cxx', 'objcxx'):
                files.append(task)
        response_file = build_framework.make_bld_node(vscode, 'response_files', '', task_gen.target + '.txt')
        response_file.parent.mkdir()
        vscode.create_task(
            'vscode_response', [], [response_file],
            include_nodes=getattr(task_gen, 'includes_nodes'),
            include_paths=[],
            defines=task_gen.env.DEFINES
        )


@waflib.TaskGen.feature('motor:vscode')
def vscode_make_compile_commands(task_gen: waflib.TaskGen.task_gen) -> None:
    for toolchain in task_gen.env.ALL_TOOLCHAINS:
        bld_env = task_gen.bld.all_envs[toolchain]
        if bld_env.SUB_TOOLCHAINS:
            env = task_gen.bld.all_envs[bld_env.SUB_TOOLCHAINS[0]]
        else:
            env = bld_env
        compiler_file_c = build_framework.make_bld_node(task_gen, 'response_files', '', 'c_' + toolchain + '.txt')
        compiler_file_c.parent.mkdir()
        compiler_sh_c = build_framework.make_bld_node(task_gen, 'compiler', '', 'c_' + toolchain + '.sh')
        compiler_bat_c = build_framework.make_bld_node(task_gen, 'compiler', '', 'c_' + toolchain + '.bat')
        compiler_py_c = build_framework.make_bld_node(task_gen, 'compiler', '', 'c_' + toolchain + '.py')
        compiler_sh_c.parent.mkdir()
        task_gen.create_task(
            'vscode_compiler', [], [compiler_file_c, compiler_sh_c, compiler_bat_c, compiler_py_c],
            target=env.COMPILER_TARGET,
            include_paths=env.COMPILER_C_INCLUDES,
            defines=env.DEFINES + env.COMPILER_C_DEFINES,
            platforms=env.VALID_PLATFORMS
        )
        compiler_file_cxx = build_framework.make_bld_node(task_gen, 'response_files', '',
                                                          'cxx_' + toolchain + '.txt')
        compiler_sh_cxx = build_framework.make_bld_node(task_gen, 'compiler', '', 'cxx_' + toolchain + '.sh')
        compiler_bat_cxx = build_framework.make_bld_node(task_gen, 'compiler', '', 'cxx_' + toolchain + '.bat')
        compiler_py_cxx = build_framework.make_bld_node(task_gen, 'compiler', '', 'cxx_' + toolchain + '.py')
        compiler_sh_cxx.parent.mkdir()
        task_gen.create_task(
            'vscode_compiler', [], [compiler_file_cxx, compiler_sh_cxx, compiler_bat_cxx, compiler_py_cxx],
            target=env.COMPILER_TARGET,
            include_paths=env.COMPILER_CXX_INCLUDES,
            defines=env.DEFINES + env.COMPILER_CXX_DEFINES,
            platforms=env.VALID_PLATFORMS
        )
        compile_commands = build_framework.make_bld_node(
            task_gen, 'compile_commands', toolchain, 'compile_commands.json'
        )
        compile_commands.parent.mkdir()
        if sys.platform == 'win32':
            compilers = compiler_bat_c, compiler_bat_cxx
        else:
            compilers = compiler_sh_c, compiler_sh_cxx
        task_gen.create_task(
            'vscode_commands', [], [compile_commands],
            bld_env=env,
            files=getattr(task_gen, 'files'),
            compiler_files=(compiler_file_c, compiler_file_cxx, compilers[0], compilers[1])
        )
    properties = build_framework.make_bld_node(task_gen, None, None, 'c_cpp_properties.json')
    task_gen.create_task('vscode_properties', [], [properties])
    tasks = build_framework.make_bld_node(task_gen, None, None, 'tasks.json')
    task_gen.create_task('vscode_tasks', [], [tasks])

    launch = build_framework.make_bld_node(task_gen, None, None, 'launch.json')
    launch_tasks = []
    for g in task_gen.bld.groups:
        for tg in g:
            if not isinstance(tg, waflib.TaskGen.task_gen):
                continue
            if 'motor:game' in tg.features or 'motor:python_module' in tg.features or 'motor:unit_test' in tg.features:
                launch_tasks.append(tg)
    task_gen.create_task('vscode_launch', [], [launch], launch_tasks=launch_tasks)
    build_framework.install_files(
        task_gen, os.path.join(task_gen.bld.srcnode.abspath(), '.vscode'), [properties, tasks, launch]
    )


@waflib.TaskGen.feature('motor:vscode:cmake')
def vscode_make_cmake(task_gen: waflib.TaskGen.task_gen) -> None:
    configurations = getattr(task_gen.bld, 'motor_cmake_tg').toolchains  # type: List[Tuple[str, waflib.Node.Node]]

    kits = build_framework.make_bld_node(task_gen, None, None, 'cmake-kits.json')
    task_gen.create_task('vscode_kits', [], [kits], toolchains=[(t[0], t[1].abspath()) for t in configurations])
    variants = build_framework.make_bld_node(task_gen, None, None, 'cmake-variants.json')
    task_gen.create_task('vscode_variants', [], [variants], variants=task_gen.env.ALL_VARIANTS)

    build_framework.install_files(
        task_gen, os.path.join(task_gen.bld.srcnode.abspath(), '.vscode'), [kits, variants]
    )

    launch = build_framework.make_bld_node(task_gen, None, None, 'launch.json')
    launch_tasks = []
    for g in task_gen.bld.groups:
        for tg in g:
            if not isinstance(tg, waflib.TaskGen.task_gen):
                continue
            if 'motor:game' in tg.features:
                launch_tasks.append(tg)
    task_gen.create_task('vscode_cmake_launch', [], [launch], launch_tasks=launch_tasks)
    build_framework.install_files(
        task_gen, os.path.join(task_gen.bld.srcnode.abspath(), '.vscode'), [launch]
    )


def build(build_context: build_framework.BuildContext) -> None:
    if 'vscode' in build_context.env.PROJECTS:
        vscode = build_context(
            group=build_context.cmd, target='projects', features=['motor:vscode'], projects={}, files=[]
        )
        setattr(build_context, 'vscode', vscode)
    if 'vscode-cmake' in build_context.env.PROJECTS:
        vscode_cmake = build_context(
            group=build_context.cmd,
            target='vscode-cmake',
            features=['motor:vscode:cmake'],
        )
        setattr(build_context, 'vscode_cmake', vscode_cmake)
