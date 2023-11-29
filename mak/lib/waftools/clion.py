import os
import sys
import build_framework
import waflib.Context
import waflib.TaskGen
from typing import Any, List, Optional, Tuple
import waftools_common.cmake

modules_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/motor.iml" filepath="$PROJECT_DIR$/.idea/motor.iml" />
    </modules>
  </component>
</project>"""

custom_compiler_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="com.jetbrains.cidr.lang.workspace.compiler.custom.CustomCompilerService">
    <option name="definitionsFile" value="$PROJECT_DIR$/.idea/custom_compiler.yaml" />
    <option name="enabled" value="true" />
  </component>
</project>"""

misc_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="CMakeWorkspace" PROJECT_DIR="$PROJECT_DIR$" />
  <component name="CidrRootsConfiguration">
    <sourceRoots>
      <file path="$PROJECT_DIR$/%s" />
      <file path="$PROJECT_DIR$/%s" />
    </sourceRoots>
    <excludeRoots>
      <file path="$PROJECT_DIR$/%s" />
      <file path="$PROJECT_DIR$/.cache" />
    </excludeRoots>configurations
  </component>
</project>"""


def _get_define(d: str) -> str:
    value_pos = d.find('=') + 1
    if value_pos:
        return '%s: %s' % (d[:value_pos - 1], d[value_pos:].replace('"', '\\"'))
    else:
        return '%s:' % d


class CLion(build_framework.ProjectGenerator):
    """
        creates projects for IntelliJ CLion
    """
    cmd = 'clion'
    variant = 'clion'

    def __init__(self, **kw: Any) -> None:
        build_framework.BuildContext.__init__(self, **kw)
        self._scopes_dir = self.motornode
        self._inspections_dir = self.motornode
        self._code_styles_dir = self.motornode
        self._run_configs_dir = self.motornode
        self._idea_dir = self.motornode

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
        self._idea_dir = self.srcnode.make_node('.idea')
        self._run_configs_dir = self._idea_dir.make_node('runConfigurations')
        self._code_styles_dir = self._idea_dir.make_node('codeStyles')
        self._inspections_dir = self._idea_dir.make_node('inspectionProfiles')
        self._scopes_dir = self._idea_dir.make_node('scopes')

        configurations = waftools_common.cmake.write_cmake_workspace(self)

        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.srcnode.name)

        self._run_configs_dir.mkdir()
        self._code_styles_dir.mkdir()
        self._scopes_dir.mkdir()
        self._inspections_dir.mkdir()

        self.write_base(appname)
        self.write_custom_compilers(configurations)
        self.write_cmake_xml(configurations)
        self.write_codestyle()
        self.write_launch_files(appname)
        return configurations

    def write_base(self, appname: str) -> None:
        with open(self._idea_dir.make_node('.name').abspath(), 'w') as name:
            name.write(appname)
        with open(self._idea_dir.make_node('modules.xml').abspath(), 'w') as modules_xml_file:
            modules_xml_file.write(modules_xml)
        with open(self._idea_dir.make_node('misc.xml').abspath(), 'w') as misc_xml_file:
            misc_xml_file.write(
                misc_xml % (
                    self.motornode.make_node('mak/lib').path_from(self.path),
                    self.motornode.make_node('mak/typeshed').path_from(self.path),
                    self.bldnode.path_from(self.path),
                )
            )
        with open(self._scopes_dir.make_node('Motor.xml').abspath(), 'w') as scopes:
            prefix = (self.motornode.path_from(self.srcnode) + '/') if self.motornode != self.srcnode else ''
            scopes.write(
                '<component name="DependencyValidationManager">\n'
                '  <scope name="Motor" pattern="'
                '((file[motor]:%(prefix)ssrc/*||file[motor]:%(prefix)ssrc//*)&amp;&amp;'
                '!file[motor]:%(prefix)ssrc/motor/3rdparty//*'
                '||file[motor]:%(prefix)sextra/*)&amp;&amp;!file[motor]:'
                '%(prefix)sextra/android/src/motor/3rdparty//*" />\n'
                '</component>\n' % {'prefix': prefix}
            )
        if not os.path.exists(self._idea_dir.make_node('motor.iml').abspath()):
            with open(self._idea_dir.make_node('motor.iml').abspath(), 'w') as motor_iml:
                motor_iml.write(
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<module classpath="CMake" type="CPP_MODULE" version="4" />\n'
                )
        for filename in ('profiles_settings.xml', 'Motor_strict.xml'):
            with open(self._inspections_dir.make_node(filename).abspath(), 'w') as inspection_file:
                with open(self.motornode.make_node('mak/tools/clion/%s' % filename).abspath(), 'r') as template_file:
                    inspection_file.write(template_file.read())

    def write_custom_compilers(self, configurations: List[Tuple[str, str]]) -> None:
        with open(self._idea_dir.make_node('custom-compiler.xml').abspath(), 'w') as custom_compiler_xml_file:
            custom_compiler_xml_file.write(custom_compiler_xml)
        with open(self._idea_dir.make_node('custom_compiler.yaml').abspath(), 'w') as custom_compiler_yaml_file:
            custom_compiler_yaml_file.write('compilers:\n')
            for toolchain_name, _ in configurations:
                bld_env = self.all_envs[toolchain_name]
                if bld_env.SUB_TOOLCHAINS:
                    env = self.all_envs[bld_env.SUB_TOOLCHAINS[0]]
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

    def write_cmake_xml(self, configurations: List[Tuple[str, str]]) -> None:
        bld_path = self.bldnode.make_node('clion').path_from(self.srcnode).replace('\\', '/')
        with open(self._idea_dir.make_node('cmake.xml').abspath(), 'w') as cmake_xml:
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
                            'toolchain': toolchain,
                            'bld_path': bld_path
                        }
                    )
            cmake_xml.write('    </configurations>\n'
                            '  </component>\n'
                            '</project>\n')

    def write_codestyle(self) -> None:
        with open(self._code_styles_dir.make_node('codeStyleConfig.xml').abspath(), 'w') as config:
            config.write(
                '<component name="ProjectCodeStyleConfiguration">\n'
                '  <state>\n'
                '    <option name="USE_PER_PROJECT_SETTINGS" value="true" />\n'
                '  </state>\n'
                '</component>'
            )
        with open(self._code_styles_dir.make_node('Project.xml').abspath(), 'w') as project:
            project.write(
                '<component name="ProjectCodeStyleConfiguration">\n'
                '  <code_scheme name="Project" version="173">\n'
                '    <clangFormatSettings>\n'
                '      <option name="ENABLED" value="true" />\n'
                '    </clangFormatSettings>\n'
                '  </code_scheme>\n'
                '</component>'
            )

    def write_launch_files(self, appname: str) -> None:
        launch_files = []
        assert self.launcher is not None
        for g in self.groups:
            for tg in g:
                if not isinstance(tg, waflib.TaskGen.task_gen):
                    continue
                if 'motor:postprocess' in tg.features:
                    continue
                node = self._run_configs_dir.make_node('motor_%s.completion.xml' % tg.name)
                launch_files.append(node)
                with open(node.path_from(self.path), 'w') as run_file:
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
                            'launcher': self.launcher.target,
                            'target': tg.name
                        }
                    )
                if 'motor:game' in tg.features:
                    node = self._run_configs_dir.make_node('motor_%s.xml' % tg.name)
                    launch_files.append(node)
                    with open(node.path_from(self.path), 'w') as run_file:
                        run_file.write(
                            '<component name="ProjectRunConfigurationManager">\n'
                            '  <configuration default="false" name="%(target)s"'
                            ' type="CMakeRunConfiguration"'
                            ' factoryName="Application"'
                            ' PROGRAM_PARAMS="%(target)s" '
                            ' REDIRECT_INPUT="false"'
                            ' ELEVATE="false"'
                            ' USE_EXTERNAL_CONSOLE="false"'
                            ' PASS_PARENT_ENVS_2="true"'
                            ' PROJECT_NAME="%(project)s"'
                            ' TARGET_NAME="%(launcher)s"'
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
                                'launcher': self.launcher.target,
                                'target': tg.name
                            }
                        )

        for env_name in self.env.ALL_TOOLCHAINS:
            for variant in self.env.ALL_VARIANTS:
                for arg in ['', 'nomaster', 'static', 'dynamic']:
                    build_filename = self._run_configs_dir.make_node(
                        'motor_build_%s_%s%s.xml' % (env_name, variant, arg)
                    )
                    launch_files.append(build_filename)
                    with open(build_filename.abspath(), 'w') as run_config:
                        run_config.write(
                            '<component name="ProjectRunConfigurationManager">\n'
                            '  <configuration default="false" name="build:%(toolchain)s:%(variant)s%(type)s"'
                            ' type="PythonConfigurationType" factoryName="Python" folderName="build%(type)s">\n'
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
                            '    <option name="SCRIPT_NAME" value="%(waf)s" />\n'
                            '    <option name="PARAMETERS" value="build:%(toolchain)s:%(variant)s '
                            '--werror %(arg)s" />\n'
                            '    <option name="SHOW_COMMAND_LINE" value="false" />\n'
                            '    <option name="EMULATE_TERMINAL" value="false" />\n'
                            '    <option name="MODULE_MODE" value="false" />\n'
                            '    <option name="REDIRECT_INPUT" value="false" />\n'
                            '    <option name="INPUT_FILE" value="" />\n'
                            '    <method v="2" />\n'
                            '  </configuration>\n'
                            '</component>\n' % {
                                'toolchain': env_name,
                                'variant': variant,
                                'type': arg and ('[%s]' % arg) or '',
                                'arg': arg and ('--%s' % arg) or '',
                                'waf': sys.argv[0]
                            }
                        )

                build_filename = self._run_configs_dir.make_node('motor_clean_%s_%s%s.xml' % (env_name, variant, arg))
                launch_files.append(build_filename)
                with open(build_filename.abspath(), 'w') as run_config:
                    run_config.write(
                        '<component name="ProjectRunConfigurationManager">\n'
                        '  <configuration default="false" name="clean:%(toolchain)s:%(variant)s"'
                        ' type="PythonConfigurationType" factoryName="Python" folderName="clean">\n'
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
                        '    <option name="SCRIPT_NAME" value="%(waf)s" />\n'
                        '    <option name="PARAMETERS" value="clean:%(toolchain)s:%(variant)s" />\n'
                        '    <option name="SHOW_COMMAND_LINE" value="false" />\n'
                        '    <option name="EMULATE_TERMINAL" value="false" />\n'
                        '    <option name="MODULE_MODE" value="false" />\n'
                        '    <option name="REDIRECT_INPUT" value="false" />\n'
                        '    <option name="INPUT_FILE" value="" />\n'
                        '    <method v="2" />\n'
                        '  </configuration>\n'
                        '</component>\n' % {
                            'toolchain': env_name,
                            'variant': variant,
                            'waf': sys.argv[0]
                        }
                    )
        node = self._run_configs_dir.make_node('motor_clion.xml')
        launch_files.append(node)
        with open(node.abspath(), 'w') as run_config:
            run_config.write(
                '<component name="ProjectRunConfigurationManager">\n'
                '  <configuration default="false" name="refresh project" type="PythonConfigurationType"'
                ' factoryName="Python">\n'
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
                '    <option name="SCRIPT_NAME" value="%(waf)s" />\n'
                '    <option name="PARAMETERS" value="clion" />\n'
                '    <option name="SHOW_COMMAND_LINE" value="false" />\n'
                '    <option name="EMULATE_TERMINAL" value="false" />\n'
                '    <option name="MODULE_MODE" value="false" />\n'
                '    <option name="REDIRECT_INPUT" value="false" />\n'
                '    <option name="INPUT_FILE" value="" />\n'
                '    <method v="2" />\n'
                '  </configuration>\n'
                '</component>\n' % {'waf': sys.argv[0]}
            )
        node = self._run_configs_dir.make_node('motor_reconfigure.xml')
        launch_files.append(node)
        with open(node.abspath(), 'w') as run_config:
            run_config.write(
                '<component name="ProjectRunConfigurationManager">\n'
                '  <configuration default="false" name="reconfigure" type="PythonConfigurationType"'
                ' factoryName="Python">\n'
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
                '    <option name="SCRIPT_NAME" value="%(waf)s" />\n'
                '    <option name="PARAMETERS" value="reconfigure" />\n'
                '    <option name="SHOW_COMMAND_LINE" value="false" />\n'
                '    <option name="EMULATE_TERMINAL" value="false" />\n'
                '    <option name="MODULE_MODE" value="false" />\n'
                '    <option name="REDIRECT_INPUT" value="false" />\n'
                '    <option name="INPUT_FILE" value="" />\n'
                '    <method v="2" />\n'
                '  </configuration>\n'
                '</component>\n' % {'waf': sys.argv[0]}
            )
        for node in self._run_configs_dir.ant_glob('motor_*.xml'):
            if node not in launch_files:
                node.delete(True)
