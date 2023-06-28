from waflib import Context, Build, TaskGen, Options, Utils
from waflib.TaskGen import task_gen
import os
import sys
import json
from json_minify import json_minify
import cmake


def vscode_path_from(path, node):
    if isinstance(path, str):
        return path
    else:
        return os.path.join('${workspaceFolder}', path.path_from(node))


class vscode_common(Build.BuildContext):
    "creates common plumbing for VSCode projects"
    cmd = '_vscode'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'

    SETTINGS = '  {\n' \
               '    "editor.formatOnSave": true,\n' \
               '    "editor.formatOnType": true,\n' \
               '    "python.linting.mypyArgs": [\n' \
               '      "--follow-imports=silent"\n' \
               '    ],\n' \
               '    "python.linting.mypyEnabled": true,\n' \
               '    "python.linting.pylintEnabled": false,\n' \
               '    "python.formatting.yapfArgs": [\n' \
               '      "--style=%(motorpath)s/setup.cfg"\n' \
               '    ],\n' \
               '    "python.formatting.autopep8Path": "yapf",\n' \
               '    "python.formatting.provider": "autopep8",\n' \
               '    "python.autoComplete.extraPaths": [\n' \
               '      "%(motorpath)s/mak/libs"\n' \
               '    ],\n' \
               '    "python.analysis.extraPaths": [\n' \
               '      "%(motorpath)s/mak/libs"\n' \
               '    ],\n' \
               '    "files.exclude": {\n' \
               '      "**/.git": true,\n' \
               '      "**/.svn": true,\n' \
               '      "**/.hg": true,\n' \
               '      "**/CVS": true,\n' \
               '      "**/.DS_Store": true,\n' \
               '      "**/__pycache__": true,\n' \
               '      "**/*.pyc": true,\n' \
               '      "bld/.waf/*-*-*": true,\n' \
               '      "bld/.waf/*.*": true,\n' \
               '      "**/.clangd": true,\n' \
               '      "**/.mypy_cache": true,\n' \
               '    },\n' \
               '    "files.watcherExclude": {\n' \
               '      "**/.git/*": true,\n' \
               '      "**/bld/**": true\n' \
               '    },\n' \
               '    "clangd.arguments": [\n' \
               '      "--header-insertion=never"\n' \
               '    ],\n' \
               '    "C_Cpp.codeAnalysis.clangTidy.enabled": true,\n' \
               '    "cmake.buildDirectory": "${workspaceFolder}/%(projectpath)s/${buildKit}/${buildType}",\n' \
               '    "cmake.showSystemKits": false\n' \
               '  }\n'

    def execute(self):
        """
        Entry point
        """
        if self.schedule_setup():
            return "SKIP"

        self.restore()
        Options.options.nomaster = True
        if not self.all_envs:
            self.load_envs()
        self.variant = self.__class__.motor_variant
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
        self.features = ['GUI']

        self.recurse([self.run_dir])
        self.write_workspace()

    def write_workspace(self):
        appname = getattr(Context.g_module, Context.APPNAME, self.srcnode.name)

        workspace_node = self.srcnode.make_node('%s.code-workspace' % appname)

        with open(workspace_node.abspath(), 'w') as workspace:
            workspace.write(
                '{\n'
                '  "folders": [\n'
                '    {\n'
                '      "path": ".",\n'
                '      "name": "%s"\n'
                '    }\n'
                '  ],\n' % appname
            )
            workspace.write(
                '  "extensions": {\n'
                '    "recommendations": [\n'
                '      %s\n'
                '    ]\n'
                '  },\n'
                '  "settings": %s\n'
                '}\n' % (
                    ',\n      '.join(self.extensions), self.SETTINGS % {
                        'motorpath': self.motornode.path_from(self.path),
                        'projectpath': self.bldnode.path_from(self.path)
                    }
                )
            )


class vscode(vscode_common):
    "creates projects for Visual Studio Code"
    cmd = 'vscode'
    variant = 'projects/vscode'
    extensions = ['"ms-vscode.cpptools"', '"ms-python.python"']

    def write_workspace(self):
        vscode_common.write_workspace(self)
        options = [a for a in sys.argv if a[0] == '-']
        tasks = []
        configurations = []
        vscode_node = self.srcnode.make_node('.vscode')
        vscode_node.mkdir()

        for env_name in self.env.ALL_TOOLCHAINS:
            toolchain_node = vscode_node.make_node('toolchains').make_node(env_name)
            bld_env = self.all_envs[env_name]
            if bld_env.SUB_TOOLCHAINS:
                env = self.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env
            for variant in self.env.ALL_VARIANTS:
                variant_node = toolchain_node.make_node(variant)
                variant_node.mkdir()
                properties = {}
                for var in [
                    'Prefix', 'TmpDir', 'Toolchain', 'Deploy_BinDir', 'Deploy_RunBinDir', 'Deploy_LibDir',
                    'Deploy_IncludeDir', 'Deploy_DataDir', 'Deploy_PluginDir', 'Deploy_KernelDir', 'Deploy_RootDir'
                ]:
                    properties[var] = bld_env[var.upper()]
                properties['Variant'] = variant
                properties['Launcher'] = env.cxxprogram_PATTERN % self.launcher.target
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
                commands = []
                include_paths = []
                defines = []
                for g in self.groups:
                    for tg in g:
                        if not isinstance(tg, TaskGen.task_gen):
                            continue
                        tg.post()
                        mark = len(commands)
                        resp_file_name_c = variant_node.make_node('%s_c.txt' % tg.name).path_from(self.srcnode)
                        resp_file_name_cxx = variant_node.make_node('%s_cxx.txt' % tg.name).path_from(self.srcnode)

                        for task in tg.tasks:
                            if task.__class__.__name__ in ('c', 'objc'):
                                commands.append(
                                    {
                                        'directory': self.path.abspath(),
                                        'arguments': env.CC + ['@%s' % (resp_file_name_c)],
                                        'file': task.inputs[0].path_from(self.path),
                                        'output': task.outputs[0].path_from(self.path)
                                    }
                                )
                            elif task.__class__.__name__ in ('cxx', 'objcxx'):
                                commands.append(
                                    {
                                        'directory': self.path.abspath(),
                                        'arguments': env.CXX + ['-std=c++14', '@%s' % resp_file_name_cxx],
                                        'file': task.inputs[0].path_from(self.path),
                                        'output': task.outputs[0].path_from(self.path)
                                    }
                                )

                        if len(commands) != mark:
                            tg_includes = []
                            tg_defines = []
                            tg_includes += getattr(tg, 'includes', [])
                            tg_includes += getattr(tg, 'export_includes', [])
                            tg_includes += getattr(tg, 'export_system_includes', [])
                            tg_includes += getattr(tg, 'extra_includes', [])
                            tg_includes = [vscode_path_from(i, self.srcnode) for i in tg_includes]
                            tg_defines += getattr(tg, 'defines', [])
                            tg_defines += getattr(tg, 'export_defines', [])
                            tg_defines += getattr(tg, 'extra_defines', [])
                            tg_defines += tg.env.DEFINES
                            with open(resp_file_name_c, 'w') as response_file:
                                response_file.write('--target=%s-%s\n' % (env.ARCHITECTURE, env.SYSTEM_NAME))
                                for i in env.COMPILER_C_INCLUDES + env.INCLUDES:
                                    response_file.write('-isystem%s\n' % i)
                                for i in tg_includes + tg.env.INCPATHS:
                                    response_file.write('-I%s\n' % i)
                                for d in env.COMPILER_C_DEFINES + env.DEFINES + tg_defines:
                                    response_file.write('-D%s\n' % d)
                            with open(resp_file_name_cxx, 'w') as response_file:
                                response_file.write('--target=%s-%s\n' % (env.ARCHITECTURE, env.SYSTEM_NAME))
                                for i in env.COMPILER_CXX_INCLUDES + env.INCLUDES:
                                    response_file.write('-isystem%s\n' % i)
                                for i in tg_includes + tg.env.INCPATHS:
                                    response_file.write('-I%s\n' % i)
                                for d in env.COMPILER_CXX_DEFINES + env.DEFINES + tg_defines:
                                    response_file.write('-D%s\n' % d)

                            include_paths += tg_includes
                            defines += tg_defines

                with open(variant_node.make_node('compile_commands.json').abspath(), 'w') as compile_commands:
                    json.dump(commands, compile_commands, indent=2)
                seen = set([self.srcnode, self.bldnode])
                configurations.append(
                    {
                        'name':
                            '%s - %s' % (env_name, variant),
                        'includePath': [i for i in include_paths if i not in seen and not seen.add(i)],
                        'defines': [d for d in defines if d not in seen and not seen.add(d)],
                        'compileCommands':
                            '${workspaceFolder}/.vscode/toolchains/%s/%s/compile_commands.json' % (env_name, variant),
                        'customConfigurationVariables':
                            properties
                    }
                )

        tasks_file = vscode_node.make_node('tasks.json')
        try:
            tasks = json.loads(json_minify(Utils.readf(tasks_file.abspath(), 'r')))
        except IOError:
            tasks = {'version': '2.0.0', 'tasks': [], 'inputs': []}
        else:
            tasks['tasks'] = [t for t in tasks['tasks'] if not t['label'].startswith('motor:')]
            try:
                tasks['inputs'] = [i for i in tasks['inputs'] if not i['id'].startswith('motor-')]
            except KeyError:
                tasks['inputs'] = []

        launch_file = vscode_node.make_node('launch.json')
        try:
            launch_config_content = json_minify(Utils.readf(launch_file.abspath(), 'r'))
        except IOError:
            launch_configs = {'version': '0.2.0', 'configurations': [], 'inputs': []}
        else:
            launch_configs = json.loads(launch_config_content)
            launch_configs['configurations'] = [
                c for c in launch_configs['configurations'] if not c['name'].startswith('motor:')
            ]
            try:
                launch_configs['inputs'] = [i for i in tasks['inputs'] if not i['id'].startswith('motor-')]
            except KeyError:
                launch_configs['inputs'] = []

        for action, command, is_default in [
            ('build', ['build:${input:motor-Toolchain}:${input:motor-Variant}', '-p'], True),
            (
                    'build[fail-tests=no]',
                    ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--no-fail-on-tests', '-p'], False
            ), ('build[static]', ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--static', '-p'], False),
            ('build[dynamic]', ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--dynamic', '-p'], False),
            ('build[nomaster]', ['build:${input:motor-Toolchain}:${input:motor-Variant}', '--nomaster', '-p'], False),
            ('build[single]', ['build:${input:motor-Toolchain}:${input:motor-Variant}', '-j', '1', '-p'], False),
            ('clean', ['clean:${input:motor-Toolchain}:${input:motor-Variant}', '-p'], False),
            (
                    'rebuild', [
                        'clean:${input:motor-Toolchain}:${input:motor-Variant}',
                        'build:${input:motor-Toolchain}:${input:motor-Variant}', '-p'
                    ], False
            ), ('setup', ['setup:${input:motor-Toolchain}'], False), ('reconfigure', ['reconfigure'], False),
            (self.cmd, [self.cmd], False)
        ]:
            tasks['tasks'].append(
                {
                    'label': 'motor:%s' % action,
                    'type': 'process',
                    'command': [sys.executable],
                    'args': [sys.argv[0]] + command + options,
                    'options': {
                        'cwd': self.srcnode.abspath()
                    },
                    'problemMatcher': ['$gcc', '$msCompile'],
                    'group': {
                        'kind': 'build',
                        'isDefault': True
                    } if is_default else 'build'
                }
            )
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

        tasks['tasks'].append(
            {
                'label': 'motor:mypy',
                'type': 'process',
                'command': [sys.executable],
                'args': ['-m', 'mypy', '--show-column-numbers', '-p', 'mypy_root'],
                'options': {
                    'cwd': self.srcnode.abspath()
                },
                'problemMatcher': ['$gcc', '$msCompile'],
                'group': 'build'
            }
        )

        for input in ('Toolchain', 'Variant'):
            tasks['inputs'].append(
                {
                    'id': 'motor-%s' % input,
                    'type': 'command',
                    'command': 'cpptools.activeConfigCustomVariable',
                    'args': input
                }
            )

        for g in self.groups:
            for tg in g:
                if not isinstance(tg, TaskGen.task_gen):
                    continue
                if 'motor:game' in tg.features:
                    launch_configs['configurations'].append(
                        {
                            'name':
                                'motor:%s' % tg.target,
                            'type':
                                'cppdbg',
                            'request':
                                'launch',
                            'program':
                                '${workspaceFolder}/${input:motor-Prefix}/${input:motor-Variant}/${input:motor-Deploy_BinDir}/${input:motor-Launcher}',
                            'args': [tg.target],
                            'cwd':
                                '${workspaceFolder}',
                            'miDebuggerPath':
                                '${input:motor-DebuggerPath}',
                            'MIMode':
                                '${input:motor-DebuggerMode}',
                            'windows': {
                                'type': 'cppvsdbg'
                            },
                            'preLaunchTask':
                                'motor:build'
                        }
                    )
                if 'motor:python_module' in tg.features:
                    launch_configs['configurations'].append(
                        {
                            'name':
                                'motor:%s' % tg.target,
                            'type':
                                'cppdbg',
                            'request':
                                'launch',
                            'program':
                                '${input:motor-Python}',
                            'miDebuggerPath':
                                '${input:motor-DebuggerPath}',
                            'MIMode':
                                '${input:motor-DebuggerMode}',
                            'args': ['-c', 'import py_motor; py_motor.run()'],
                            'cwd':
                                '${workspaceFolder}/${input:motor-Prefix}/${input:motor-Variant}/${input:motor-Deploy_RunBinDir}',
                            'windows': {
                                'type': 'cppvsdbg'
                            },
                            'preLaunchTask':
                                'motor:build'
                        }
                    )
                if 'motor:unit_test' in tg.features:
                    unit_test = tg.link_task.outputs[0].path_from(tg.bld.bldnode)
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

        for input in (
                'Toolchain', 'Variant', 'Prefix', 'Deploy_RunBinDir', 'Deploy_BinDir', 'Launcher', 'Python',
                'DebuggerPath',
                'DebuggerMode', 'TmpDir'
        ):
            launch_configs['inputs'].append(
                {
                    'id': 'motor-%s' % input,
                    'type': 'command',
                    'command': 'cpptools.activeConfigCustomVariable',
                    'args': input
                }
            )

        with open(vscode_node.make_node('c_cpp_properties.json').abspath(), 'w') as conf_file:
            json.dump({'configurations': configurations}, conf_file, indent=2)
        with open(tasks_file.abspath(), 'w') as document:
            json.dump(tasks, document, indent=2)
        with open(launch_file.abspath(), 'w') as document:
            json.dump(launch_configs, document, indent=2)


class vscode_cmake(vscode_common):
    "creates projects for Visual Studio Code using CMake"
    cmd = 'vscode_cmake'
    variant = 'projects/vscode'
    extensions = ['"ms-vscode.cpptools"', '"ms-python.python"', '"ms-vscode.cmake-tools"']

    def write_workspace(self):
        vscode_common.write_workspace(self)
        toolchains = cmake.write_cmake_workspace(self, [a for a in sys.argv if a[0] == '-'])
        vscode_node = self.srcnode.make_node('.vscode')
        vscode_node.mkdir()

        with open(vscode_node.make_node('cmake-kits.json').abspath(), 'w') as kits:
            kits.write(
                '[\n'
                '%s\n'
                ']' %
                ',\n'.join('  {\n'
                           '    "name": "%s",\n'
                           '    "toolchainFile": "%s"\n'
                           '  }' % t for t, _ in toolchains)
            )

        with open(vscode_node.make_node('cmake-variants.json').abspath(), 'w') as variants:
            variants.write(
                '{\n'
                '  "buildTypes": {\n'
                '    "default": "%s",\n'
                '    "description": "build types",\n'
                '    "choices": {\n'
                '      %s\n'
                '    }\n'
                '  }\n'
                '}' % (
                    self.env.ALL_VARIANTS[0], ',\n'.join(
                        '      "%(variant)s": {\n'
                        '        "short": "%(variant)s",\n'
                        '        "long": "build %(variant)s",\n'
                        '        "buildType": "%(variant)s"\n'
                        '      }' % {'variant': variant} for variant in self.env.ALL_VARIANTS
                    )
                )
            )

        launch_file = vscode_node.make_node('launch.json')
        try:
            launch_config_content = json_minify(Utils.readf(launch_file.abspath(), 'r'))
        except IOError:
            launch_configs = {'version': '0.2.0', 'configurations': [], 'inputs': []}
        else:
            launch_configs = json.loads(launch_config_content)
            launch_configs['configurations'] = [
                c for c in launch_configs['configurations'] if not c['name'].startswith('motor:')
            ]

        debuggers = set()
        for env_name in self.env.ALL_TOOLCHAINS:
            bld_env = self.all_envs[env_name]
            if bld_env.GDB:
                debuggers.add(('gdb', 'cppdbg', 'gdb'))
            if bld_env.LLDB:
                debuggers.add(('lldb', 'cppdbg', 'lldb'))
            if bld_env.CDB:
                debuggers.add(('cdb', 'cppvsdbg', ''))

        for g in self.groups:
            for tg in g:
                if not isinstance(tg, TaskGen.task_gen):
                    continue
                if 'motor:game' in tg.features:
                    for name, category, type in debuggers:
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
                if 'motor:python_module' in tg.features:
                    for name, category, type in debuggers:
                        launch_configs['configurations'].append(
                            {
                                'name': 'motor:%s[%s]' % (tg.target, name),
                                'type': category,
                                'request': 'launch',
                                'program': sys.executable,
                                'args': ['-c', 'import py_motor; py_motor.run()'],
                                'cwd':
                                    '${workspaceFolder}/${input:motor-Prefix}/${input:motor-Variant}/${input:motor-Deploy_RunBinDir}',
                                'preLaunchTask':
                                    '${command:cmake.tasksBuildCommand}'
                            }
                        )

        with open(launch_file.abspath(), 'w') as document:
            json.dump(launch_configs, document, indent=2)