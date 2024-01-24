import os.path
import sys
import build_framework
import waflib.Task
import waflib.TaskGen
from typing import List, Optional, Tuple


def _get_define(d: str) -> str:
    value_pos = d.find('=') + 1
    if value_pos:
        return '%s: %s' % (d[:value_pos - 1], d[value_pos:].replace('"', '\\"'))
    else:
        return '%s:' % d


class clion_name(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)
        with open(self.outputs[0].abspath(), 'w') as name:
            name.write(appname)
        return None


class clion_modules(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as modules:
            modules.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<project version="4">\n'
                '  <component name="ProjectModuleManager">\n'
                '    <modules>\n'
                '      <module fileurl="file://$PROJECT_DIR$/.idea/motor.iml" filepath="$PROJECT_DIR$/.idea/motor.iml" />\n'
                '    </modules>\n'
                '  </component>\n'
                '</project>'
            )
        return None


class clion_compiler(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        for toolchain_name in self.env.ALL_TOOLCHAINS:
            bld_env = self.generator.bld.all_envs[toolchain_name]
            if bld_env.SUB_TOOLCHAINS:
                env = self.generator.bld.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env
            self.m.update(env.ARCHITECTURE.encode())
            self.m.update(env.SYSTEM_NAME.encode())
            self.m.update(';'.join(env.COMPILER_C_INCLUDES).encode())
            self.m.update(';'.join(env.COMPILER_C_DEFINES).encode())
            self.m.update(';'.join(env.COMPILER_CXX_INCLUDES).encode())
            self.m.update(';'.join(env.COMPILER_CXX_DEFINES).encode())

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as compiler_xml:
            compiler_xml.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<project version="4">\n'
                '  <component name="com.jetbrains.cidr.lang.workspace.compiler.custom.CustomCompilerService">\n'
                '    <option name="definitionsFile" value="$PROJECT_DIR$/.idea/custom_compiler.yaml" />\n'
                '    <option name="enabled" value="true" />\n'
                '  </component>\n'
                '</project>\n'
            )
        with open(self.outputs[1].abspath(), 'w') as custom_compiler_yaml_file:
            custom_compiler_yaml_file.write('compilers:\n')
            for toolchain_name in self.env.ALL_TOOLCHAINS:
                bld_env = self.generator.bld.all_envs[toolchain_name]
                if bld_env.SUB_TOOLCHAINS:
                    env = self.generator.bld.all_envs[bld_env.SUB_TOOLCHAINS[0]]
                else:
                    env = bld_env

                custom_compiler_yaml_file.write(
                    '  - description: %(toolchain_name)s\n'
                    '    match-language: C\n'
                    '    match-compiler-exe: .*\n'
                    '    match-args: -U%(toolchain_name)s\n'
                    '    code-insight-target-name: %(arch)s-%(system)s\n'
                    '    defines:\n'
                    '      %(defines_c)s\n'
                    '    include-dirs:\n'
                    '      - %(includes_c)s\n'
                    '  - description: %(toolchain_name)s\n'
                    '    match-language: CPP\n'
                    '    match-compiler-exe: .*\n'
                    '    match-args: -U%(toolchain_name)s\n'
                    '    code-insight-target-name: %(arch)s-%(system)s\n'
                    '    defines:\n'
                    '      %(defines_cxx)s\n'
                    '    include-dirs:\n'
                    '      - %(includes_cxx)s\n'
                    '' % {
                        'toolchain_name': toolchain_name,
                        'arch': env.ARCHITECTURE,
                        'system': env.SYSTEM_NAME,
                        'includes_c': '\n      - '.join([i for i in env.COMPILER_C_INCLUDES]),
                        'defines_c': '\n      '.join([_get_define(d) for d in env.COMPILER_C_DEFINES]),
                        'includes_cxx': '\n      - '.join([i for i in env.COMPILER_CXX_INCLUDES]),
                        'defines_cxx': '\n      '.join([_get_define(d) for d in env.COMPILER_CXX_DEFINES]),
                    }
                )
        return None


class clion_workspace(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as workspace:
            workspace.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<project version="4">\n'
                '  <component name="ClangdSettings">\n'
                '    <option name="clangWarnings" value="-Wunused-variable,-Werror=implicit-function-declaration,'
                '-Wshadow,-Wno-shadow-field-in-constructor-modified,-Wno-shadow-ivar,-Wuninitialized,-Wunused-label,'
                '-Wunused-lambda-capture,-Wno-unknown-attributes" />\n'
                '  </component>\n'
                '  <component name="FormatOnSaveOptions">\n'
                '    <option name="myRunOnSave" value="true" />\n'
                '  </component>\n'
                '</project>\n'
            )
        return None


class clion_misc(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as modules:
            motornode = getattr(self.generator.bld, 'motornode')  # type: waflib.Node.Node
            modules.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<project version="4">\n'
                '  <component name="CMakeWorkspace" PROJECT_DIR="$PROJECT_DIR$" />\n'
                '  <component name="CidrRootsConfiguration">\n'
                '    <sourceRoots>\n'
                '      <file path="$PROJECT_DIR$/%s" />\n'
                '      <file path="$PROJECT_DIR$/%s" />\n'
                '    </sourceRoots>\n'
                '    <excludeRoots>\n'
                '      <file path="$PROJECT_DIR$/%s" />\n'
                '      <file path="$PROJECT_DIR$/.cache" />\n'
                '    </excludeRoots>configurations\n'
                '  </component>\n'
                '</project>\n'
                '' % (
                    motornode.make_node('mak/lib').path_from(self.generator.bld.srcnode),
                    motornode.make_node('mak/typeshed').path_from(self.generator.bld.srcnode),
                    self.generator.bld.bldnode.path_from(self.generator.bld.srcnode),
                )
            )
        return None


class clion_scope(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        motornode = getattr(self.generator.bld, 'motornode')  # type: waflib.Node.Node
        prefix = (motornode.path_from(
            self.generator.bld.srcnode) + '/') if motornode != self.generator.bld.srcnode else ''
        with open(self.outputs[0].abspath(), 'w') as scope:
            scope.write(
                '<component name="DependencyValidationManager">\n'
                '  <scope name="Motor" pattern="'
                '((file[motor]:%(prefix)ssrc/*||file[motor]:%(prefix)ssrc//*)&amp;&amp;'
                '!file[motor]:%(prefix)ssrc/motor/3rdparty//*'
                '||file[motor]:%(prefix)sextra/*)&amp;&amp;!file[motor]:'
                '%(prefix)sextra/android/src/motor/3rdparty//*" />\n'
                '</component>\n' % {'prefix': prefix}
            )
        return None


class clion_iml(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as iml:
            iml.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<module classpath="CMake" type="CPP_MODULE" version="4" />\n'
            )
        return None


class clion_codestyle(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        motornode = getattr(self.generator.bld, 'motornode')  # type: waflib.Node.Node
        prefix = (motornode.path_from(
            self.generator.bld.srcnode) + '/') if motornode != self.generator.bld.srcnode else ''
        with open(self.outputs[0].abspath(), 'w') as config:
            config.write(
                '<component name="ProjectCodeStyleConfiguration">\n'
                '  <state>\n'
                '    <option name="USE_PER_PROJECT_SETTINGS" value="true" />\n'
                '  </state>\n'
                '</component>'
            )
        with open(self.outputs[1].abspath(), 'w') as project:
            project.write(
                '<component name="ProjectCodeStyleConfiguration">\n'
                '  <code_scheme name="Project" version="173">\n'
                '    <option name="DO_NOT_FORMAT">\n'
                '      <list>\n'
                '        <fileSet type="globPattern" pattern="%smak/vendor/**/*" />\n'
                '      </list>\n'
                '    </option>\n'
                '    <clangFormatSettings>\n'
                '      <option name="ENABLED" value="true" />\n'
                '    </clangFormatSettings>\n'
                '  </code_scheme>\n'
                '</component>'
                '' % prefix
            )
        return None


@build_framework.autosig_env('ALL_TOOLCHAINS')
class clion_cmake(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        bld_path = self.generator.bld.bldnode.make_node('clion.bld').path_from(self.generator.bld.srcnode).replace('\\',
                                                                                                                   '/')
        configurations = getattr(self.generator.bld,
                                 'motor_cmake_tg').toolchains  # type: List[Tuple[str, waflib.Node.Node]]
        with open(self.outputs[0].abspath(), 'w') as cmake_xml:
            cmake_xml.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<project version="4">\n'
                '  <component name="CMakeSharedSettings">\n'
                '    <configurations>\n'
            )
            for toolchain_name, toolchain in configurations:
                for variant in self.env.ALL_VARIANTS:
                    cmake_xml.write(
                        '      <configuration PROFILE_NAME="%(toolchain_name)s:%(variant)s"'
                        ' ENABLED="true"'
                        ' GENERATION_DIR="%(bld_path)s/%(toolchain_name)s/%(variant)s"'
                        ' CONFIG_NAME="%(variant)s"'
                        ' GENERATION_OPTIONS='
                        '"-DCMAKE_TOOLCHAIN_FILE=%(toolchain)s" />\n' % {
                            'toolchain_name': toolchain_name,
                            'variant': variant,
                            'toolchain': toolchain.abspath(),
                            'bld_path': bld_path
                        }
                    )
            cmake_xml.write('    </configurations>\n'
                            '  </component>\n'
                            '</project>\n')

        return None


class clion_run(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as run_file:
            appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)
            run_file.write(
                '<component name="ProjectRunConfigurationManager">\n'
                '  <configuration\n'
                '      default="false" name="%(target)s"'
                '      type="CMakeRunConfiguration"'
                '      factoryName="Application"'
                '      PROGRAM_PARAMS="%(target)s" '
                '      REDIRECT_INPUT="false"'
                '      ELEVATE="false"'
                '      USE_EXTERNAL_CONSOLE="false"'
                '      PASS_PARENT_ENVS_2="true"'
                '      PROJECT_NAME="%(project)s"'
                '      TARGET_NAME="%(launcher)s"'
                '      RUN_TARGET_PROJECT_NAME="%(project)s"'
                '      RUN_TARGET_NAME="%(launcher)s"\n'
                '  >\n'
                '    <method v="2">\n'
                '      <option\n'
                '          name="com.jetbrains.cidr.execution.CidrBuildBeforeRunTaskProvider$BuildBeforeRunTask"\n'
                '          enabled="true"\n'
                '      />\n'
                '    </method>\n'
                '  </configuration>\n'
                '</component>\n' % {
                    'project': appname,
                    'launcher': getattr(self, 'launcher'),
                    'target': getattr(self, 'target')
                }
            )
        return None


class clion_completion(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as run_file:
            appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)
            run_file.write(
                '<component name="ProjectRunConfigurationManager">\n'
                '  <configuration default="false" name="%(target)s.completion"'
                ' folderName=".completion"'
                ' type="CMakeRunConfiguration"'
                ' factoryName="Application"'
                ' PROGRAM_PARAMS="" '
                ' REDIRECT_INPUT="false"'
                ' ELEVATE="false"'
                ' USE_EXTERNAL_CONSOLE="false"'
                ' PASS_PARENT_ENVS_2="true"'
                ' PROJECT_NAME="%(project)s"'
                ' TARGET_NAME="%(target)s.completion"'
                ' RUN_TARGET_PROJECT_NAME="%(project)s"'
                ' RUN_TARGET_NAME="%(launcher)s">\n'
                '    <method v="2">\n'
                '      <option'
                ' name="com.jetbrains.cidr.execution.CidrBuildBeforeRunTaskProvider$'
                'BuildBeforeRunTask" enabled="true" />\n'
                '    </method>\n'
                '  </configuration>\n'
                '</component>\n' % {
                    'project': appname,
                    'launcher': getattr(self, 'launcher'),
                    'target': getattr(self, 'target')
                }
            )
        return None


@build_framework.autosig_vars('folder')
class clion_build(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        self.m.update(getattr(self, 'module', '').encode())
        self.m.update(getattr(self, 'command', '').encode())
        self.m.update(getattr(self, 'command_name', '').encode())
        self.m.update(getattr(self, 'arg', '').encode())
        self.m.update(getattr(self, 'arg_name', '').encode())

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as run_file:
            appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)
            module = getattr(self, 'module', sys.argv[0])  # type: str
            command = getattr(self, 'command', '')  # type: str
            command_name = getattr(self, 'command_name', command or module)  # type: str
            arg = getattr(self, 'arg', '')  # type: str
            arg_name = getattr(self, 'arg_name', '')  # type: str
            folder = getattr(self, 'folder')  # type: str
            if folder:
                folder = ' folderName="%s"' % folder
            run_file.write(
                '<component name="ProjectRunConfigurationManager">\n'
                '  <configuration default="false" name="%(command_name)s"'
                ' type="PythonConfigurationType" factoryName="Python"%(folder)s>\n'
                '    <module name="motor" />\n'
                '    <option name="INTERPRETER_OPTIONS" value="" />\n'
                '    <option name="PARENT_ENVS" value="true" />\n'
                '    <envs>\n'
                '      <env name="PYTHONUNBUFFERED" value="1" />\n'
                '    </envs>\n'
                '    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />\n'
                '    <option name="IS_MODULE_SDK" value="true" />\n'
                '    <option name="ADD_CONTENT_ROOTS" value="true" />\n'
                '    <option name="ADD_SOURCE_ROOTS" value="true" />\n'
                '    <option name="SCRIPT_NAME" value="%(module)s" />\n'
                '    <option name="PARAMETERS" value="%(command)s %(arg)s" />\n'
                '    <option name="SHOW_COMMAND_LINE" value="false" />\n'
                '    <option name="EMULATE_TERMINAL" value="true" />\n'
                '    <option name="MODULE_MODE" value="%(module_mode)s" />\n'
                '    <option name="REDIRECT_INPUT" value="false" />\n'
                '    <option name="INPUT_FILE" value="" />\n'
                '    <method v="2" />\n'
                '  </configuration>\n'
                '</component>\n' % {
                    'type': arg_name,
                    'arg': arg,
                    'module': module,
                    'command': command,
                    'command_name': command_name,
                    'folder': folder,
                    'module_mode': 'true' if command == '' else 'false'
                }
            )
        return None


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
@waflib.TaskGen.after_method('apply_link')
def make_clion_completion_tg(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'clion' in task_gen.bld.env.PROJECTS:
        clion_project = getattr(task_gen.bld, 'clion_project')  # type: waflib.TaskGen.task_gen
        launcher = getattr(task_gen.bld, 'launcher')  # type: waflib.TaskGen.task_gen
        idea_dir = task_gen.bld.srcnode.make_node('.idea')
        run_configs_dir = idea_dir.make_node('runConfigurations')
        launch_file = build_framework.make_bld_node(clion_project, 'runConfigurations', None,
                                                    'motor_%s.completion.xml' % task_gen.target)
        clion_project.create_task('clion_completion', [], [launch_file], target=task_gen.target,
                                  launcher=launcher.target)
        build_framework.install_files(clion_project, run_configs_dir.abspath(), [launch_file])


@waflib.TaskGen.feature('motor:game')
@waflib.TaskGen.after_method('apply_link')
def make_clion_run_tg(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'clion' in task_gen.bld.env.PROJECTS:
        clion_project = getattr(task_gen.bld, 'clion_project')  # type: waflib.TaskGen.task_gen
        launcher = getattr(task_gen.bld, 'launcher')  # type: waflib.TaskGen.task_gen
        idea_dir = task_gen.bld.srcnode.make_node('.idea')
        run_configs_dir = idea_dir.make_node('runConfigurations')
        launch_file = build_framework.make_bld_node(clion_project, 'runConfigurations', None,
                                                    'motor_%s.xml' % task_gen.target)
        clion_project.create_task('clion_run', [], [launch_file], target=task_gen.target, launcher=launcher.target)
        build_framework.install_files(clion_project, run_configs_dir.abspath(), [launch_file])


@waflib.TaskGen.feature('motor:clion')
def make_clion_project(task_gen: waflib.TaskGen.task_gen) -> None:
    idea_dir = task_gen.bld.srcnode.make_node('.idea')
    run_configs_dir = idea_dir.make_node('runConfigurations')
    code_styles_dir = idea_dir.make_node('codeStyles')
    inspections_dir = idea_dir.make_node('inspectionProfiles')
    scopes_dir = idea_dir.make_node('scopes')

    workspace = build_framework.make_bld_node(task_gen, None, None, 'workspace.xml')
    task_gen.create_task('clion_workspace', [], [workspace])
    if not os.path.isfile(os.path.join(idea_dir.abspath(), workspace.name)):
        build_framework.install_files(task_gen, idea_dir.abspath(), [workspace])

    name = build_framework.make_bld_node(task_gen, None, None, '.name')
    task_gen.create_task('clion_name', [], [name])
    modules = build_framework.make_bld_node(task_gen, None, None, 'modules.xml')
    task_gen.create_task('clion_modules', [], [modules])
    misc = build_framework.make_bld_node(task_gen, None, None, 'misc.xml')
    task_gen.create_task('clion_misc', [], [misc])
    iml = build_framework.make_bld_node(task_gen, None, None, 'motor.iml')
    task_gen.create_task('clion_iml', [], [iml])
    if not os.path.isfile(os.path.join(idea_dir.abspath(), iml.name)):
        build_framework.install_files(task_gen, idea_dir.abspath(), [iml])
    custom_compiler_xml = build_framework.make_bld_node(task_gen, None, None, 'custom-compiler.xml')
    custom_compiler_yaml = build_framework.make_bld_node(task_gen, None, None, 'custom_compiler.yaml')
    task_gen.create_task('clion_compiler', [], [custom_compiler_xml, custom_compiler_yaml])
    cmake_xml = build_framework.make_bld_node(task_gen, None, None, 'cmake.xml')
    task_gen.create_task('clion_cmake', [], [cmake_xml])

    code_style = build_framework.make_bld_node(task_gen, 'codestyle', None, 'codeStyleConfig.xml')
    project = build_framework.make_bld_node(task_gen, 'codestyle', None, 'Project.xml')
    code_style.parent.mkdir()
    task_gen.create_task('clion_codestyle', [], [code_style, project])

    scope = build_framework.make_bld_node(task_gen, 'scope', None, 'Motor.xml')
    scope.parent.mkdir()
    task_gen.create_task('clion_scope', [], [scope])

    build_framework.install_files(task_gen, idea_dir.abspath(),
                                  [name, modules, misc, custom_compiler_xml, custom_compiler_yaml, cmake_xml])
    build_framework.install_files(task_gen, code_styles_dir.abspath(), [code_style, project])
    build_framework.install_files(task_gen, scopes_dir.abspath(), [scope])

    template_dir = getattr(task_gen.bld, 'motornode').make_node('mak/tools/clion')
    build_framework.install_files(task_gen, inspections_dir.abspath(), template_dir.ant_glob('*'))

    run_files = []
    for env_name in task_gen.env.ALL_TOOLCHAINS:
        for variant in task_gen.env.ALL_VARIANTS:
            for arg in ['', 'nomaster', 'static', 'dynamic']:
                if arg:
                    arg_name = '[' + arg + ']'
                else:
                    arg_name = ''
                folder = 'build' + arg_name
                launch_file = build_framework.make_bld_node(task_gen, 'runConfigurations', None,
                                                            'motor_build_%s_%s%s.xml' % (env_name, variant, arg))
                launch_file.parent.mkdir()
                task_gen.create_task(
                    'clion_build',
                    [],
                    [launch_file],
                    command='build:%s:%s' % (env_name, variant),
                    command_name='build:%s:%s%s' % (env_name, variant, arg_name),
                    arg=' --werror --%s' % arg,
                    arg_name=arg_name,
                    folder=folder
                )
                run_files.append(launch_file)
            launch_file = build_framework.make_bld_node(task_gen, 'runConfigurations', None,
                                                        'motor_clean_%s_%s.xml' % (env_name, variant))
            launch_file.parent.mkdir()
            task_gen.create_task(
                'clion_build',
                [],
                [launch_file],
                command='clean:%s:%s' % (env_name, variant),
                folder='clean'
            )
            run_files.append(launch_file)
        launch_file = build_framework.make_bld_node(task_gen, 'runConfigurations', None,
                                                    'motor_setup_%s.xml' % (env_name))
        launch_file.parent.mkdir()
        task_gen.create_task(
            'clion_build',
            [],
            [launch_file],
            command='setup:%s' % (env_name),
            folder='setup'
        )
        run_files.append(launch_file)
        
    launch_file = build_framework.make_bld_node(task_gen, 'runConfigurations', None, 'motor_clion.xml')
    launch_file.parent.mkdir()
    task_gen.create_task('clion_build', [], [launch_file], command='clion', folder='')
    run_files.append(launch_file)

    launch_file = build_framework.make_bld_node(task_gen, 'runConfigurations', None, 'motor_reconfigure.xml')
    launch_file.parent.mkdir()
    task_gen.create_task('clion_build', [], [launch_file], command='reconfigure', folder='')
    run_files.append(launch_file)

    launch_file = build_framework.make_bld_node(task_gen, 'runConfigurations', None, 'motor_mypy.xml')
    launch_file.parent.mkdir()
    task_gen.create_task('clion_build', [], [launch_file], module='mypy', folder='')
    run_files.append(launch_file)

    build_framework.install_files(task_gen, run_configs_dir.abspath(), run_files)


def build(build_context: build_framework.BuildContext) -> None:
    if 'clion' in build_context.env.PROJECTS:
        clion_project = build_context('clion', target='clion', group='clion', features=['motor:clion'])
        setattr(build_context, 'clion_project', clion_project)
