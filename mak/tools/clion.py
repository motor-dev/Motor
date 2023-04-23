import os.path
import sys

from waflib import Context, Build, TaskGen, Options


def clion_path_from(path, node):
    if isinstance(path, str):
        return path.replace('\\', '/')
    else:
        return path.path_from(node).replace('\\', '/')


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
    </sourceRoots>
    <excludeRoots>
      <file path="$PROJECT_DIR$/%s" />
    </excludeRoots>
  </component>
</project>"""


def get_define(d):
    value_pos = d.find('=') + 1
    if value_pos:
        return '%s: %s' % (d[:value_pos - 1], d[value_pos:].replace('"', '\\"'))
    else:
        return '%s:' % d


class CLion(Build.BuildContext):
    """
        creates projects for IntelliJ CLion
    """
    cmd = 'clion'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/clion'

    def __init__(self, **kw):
        Build.BuildContext.__init__(self, **kw)
        self.features = ['GUI']

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

        configurations = []
        files = []
        bld_path = self.bldnode.path_from(self.srcnode).replace('\\', '/')
        idea_dir = self.srcnode.make_node('.idea')
        run_configs_dir = idea_dir.make_node('runConfigurations')
        code_styles_dir = idea_dir.make_node('codeStyles')
        scopes_dir = idea_dir.make_node('scopes')
        run_configs_dir.mkdir()
        code_styles_dir.mkdir()
        scopes_dir.mkdir()
        with open(idea_dir.make_node('.name').abspath(), 'w') as name:
            name.write(appname)
        with open(idea_dir.make_node('modules.xml').abspath(), 'w') as modules_xml_file:
            modules_xml_file.write(modules_xml)
        with open(idea_dir.make_node('misc.xml').abspath(), 'w') as misc_xml_file:
            misc_xml_file.write(misc_xml % (
                self.motornode.make_node('mak/libs').path_from(self.path),
                self.bldnode.parent.parent.path_from(self.path)
            ))
        with open(scopes_dir.make_node('Motor.xml').abspath(), 'w') as scopes:
            prefix = (self.motornode.path_from(self.srcnode) + '/') if self.motornode != self.srcnode else ''
            scopes.write(
                '<component name="DependencyValidationManager">\n'
                '  <scope name="Motor" pattern="'
                '((file[motor]:%(prefix)ssrc/*||file[motor]:%(prefix)ssrc//*)&amp;&amp;'
                '!file[motor]:%(prefix)ssrc/motor/3rdparty//*'
                '||file[motor]:%(prefix)sextra/*)&amp;&amp;!file[motor]:'
                '%(prefix)sextra/android/src/motor/3rdparty//*" />\n'
                '</component>\n' % {
                    'prefix': prefix
                }
            )
        if not os.path.exists(idea_dir.make_node('motor.iml').abspath()):
            with open(idea_dir.make_node('motor.iml').abspath(), 'w') as motor_iml:
                motor_iml.write(
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<module classpath="CMake" type="CPP_MODULE" version="4" />\n'
                )
        with open(idea_dir.make_node('custom-compiler.xml').abspath(), 'w') as custom_compiler_xml_file:
            custom_compiler_xml_file.write(custom_compiler_xml)
        with open(idea_dir.make_node('custom_compiler.yaml').abspath(), 'w') as custom_compiler_yaml_file:
            custom_compiler_yaml_file.write('compilers:\n')
            for env_name in self.env.ALL_TOOLCHAINS:
                bld_env = self.all_envs[env_name]
                if bld_env.SUB_TOOLCHAINS:
                    env = self.all_envs[bld_env.SUB_TOOLCHAINS[0]]
                else:
                    env = bld_env
                dir_node = self.bldnode.make_node(env_name)
                dir_node.mkdir()
                c_shell_script = dir_node.make_node('CMake.toolchain.c.sh').abspath()
                cxx_shell_script = dir_node.make_node('CMake.toolchain.cxx.sh').abspath()
                with open(c_shell_script, 'w') as script:
                    script.write('#! /bin/sh\n')
                with open(cxx_shell_script, 'w') as script:
                    script.write('#! /bin/sh\n')

                os.chmod(c_shell_script, 0o775)
                os.chmod(cxx_shell_script, 0o775)

                custom_compiler_yaml_file.write(
                    '  - description: %(env_name)s\n'
                    '    match-language: C\n'
                    '    match-compiler-exe: %(compiler_c)s\n'
                    '    include-dirs:\n'
                    '      - %(includes)s\n'
                    '    defines:\n'
                    '      %(defines)s\n'
                    '  - description: %(env_name)s\n'
                    '    match-language: CPP\n'
                    '    match-compiler-exe: %(compiler_cxx)s\n'
                    '    include-dirs:\n'
                    '      - %(includes)s\n'
                    '    defines:\n'
                    '      %(defines)s\n' % {
                        'env_name': env_name,
                        'compiler_c': c_shell_script,
                        'compiler_cxx': cxx_shell_script,
                        'includes': '\n      - '.join([i for i in env.INCLUDES + env.COMPILER_INCLUDES]),
                        'defines': '\n      '.join([get_define(d) for d in env.DEFINES + env.COMPILER_DEFINES]),
                    })

        with open(idea_dir.make_node('cmake.xml').abspath(), 'w') as cmake_xml:
            cmake_xml.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<project version="4">\n'
                '  <component name="CMakeSharedSettings">\n'
                '    <configurations>\n'
            )
            for env_name in self.env.ALL_TOOLCHAINS:
                dir_node = self.bldnode.make_node(env_name)
                c_shell_script = dir_node.make_node('CMake.toolchain.c.sh').abspath()
                cxx_shell_script = dir_node.make_node('CMake.toolchain.cxx.sh').abspath()
                for variant in self.env.ALL_VARIANTS:
                    cmake_xml.write(
                        '      <configuration PROFILE_NAME="%(toolchain)s:%(variant)s"'
                        ' ENABLED="true"'
                        ' GENERATION_DIR="%(bld_path)s/%(toolchain)s/%(variant)s"'
                        ' CONFIG_NAME="%(toolchain)s-%(variant)s"'
                        ' GENERATION_OPTIONS='
                        '"-DCMAKE_C_COMPILER=%(compiler_c)s -DCMAKE_CXX_COMPILER=%(compiler_cxx)s" />\n' % {
                            'toolchain': env_name,
                            'variant': variant,
                            'compiler_c': c_shell_script,
                            'compiler_cxx': cxx_shell_script,
                            'bld_path': bld_path
                        }
                    )
            cmake_xml.write('    </configurations>\n'
                            '  </component>\n'
                            '</project>\n')

        with open(code_styles_dir.make_node('codeStyleConfig.xml').abspath(), 'w') as config:
            config.write(
                '<component name="ProjectCodeStyleConfiguration">\n'
                '  <state>\n'
                '    <option name="USE_PER_PROJECT_SETTINGS" value="true" />\n'
                '  </state>\n'
                '</component>'
            )
        with open(code_styles_dir.make_node('Project.xml').abspath(), 'w') as project:
            project.write(
                '<component name="ProjectCodeStyleConfiguration">\n'
                '  <code_scheme name="Project" version="173">\n'
                '    <clangFormatSettings>\n'
                '      <option name="ENABLED" value="true" />\n'
                '    </clangFormatSettings>\n'
                '  </code_scheme>\n'
                '</component>'
            )
        with open('cmake-variants.yaml', 'w') as variants:
            variants.write(
                'buildType:\n'
                '  default: %s-%s\n'
                '  choices:\n' % (self.env.ALL_TOOLCHAINS[0], self.env.ALL_VARIANTS[0])
            )
            for env_name in self.env.ALL_TOOLCHAINS:
                for variant in self.env.ALL_VARIANTS:
                    configurations.append('%s-%s' % (env_name, variant))
                    files.append('include(%s/%s/%s/CMakeLists.txt)' % (bld_path, env_name, variant))
                    variants.write('    %s-%s:\n' % (env_name, variant))
                    variants.write('      short: %s:%s\n' % (env_name, variant))
                    variants.write('      buildType: %s-%s\n' % (env_name, variant))

        with open('CMakeLists.txt', 'w') as CMakeLists:
            lists = []
            for g in self.groups:
                for tg in g:
                    if not isinstance(tg, TaskGen.task_gen):
                        continue
                    tg.post()
                    lists.append('set(%s_SOURCES "")' % tg.name)
            CMakeLists.write(
                'cmake_minimum_required(VERSION 3.15)\n'
                'project(%s)\n'
                'set(CMAKE_CONFIGURATION_TYPES "%s" CACHE STRING "" FORCE)\n\n'
                'set(CMAKE_CXX_STANDARD 14)\n'
                'set(CMAKE_CXX_STANDARD_REQUIRED ON)\n'
                'set(CMAKE_CXX_EXTENSIONS OFF)\n'
                'set_property(GLOBAL PROPERTY TARGET_MESSAGES OFF)\n'
                'set_property(GLOBAL PROPERTY RULE_MESSAGES OFF)\n'
                '%s\n'
                '%s\n'
                '\n' % (appname, ';'.join(configurations), '\n'.join(lists), '\n'.join(files))
            )

            special_files = {}
            for g in self.groups:
                for tg in g:
                    if not isinstance(tg, TaskGen.task_gen):
                        continue
                    tg.post()
                    special_files_tg = []
                    special_files[tg] = special_files_tg

                    files = []
                    for task in tg.tasks:
                        if task.__class__.__name__ in ('c', 'objc', 'cxx', 'objcxx', 'cpuc'):
                            _, had_filter = tg.apply_source_filter(tg.env, task.inputs[0])
                            if not had_filter:
                                files.append(task.inputs[0].path_from(self.path).replace('\\', '/'))
                            else:
                                special_files_tg.append(task.inputs[0])

                    if files or special_files_tg:
                        if files:
                            CMakeLists.write(
                                'list(APPEND %s_SOURCES\n'
                                '    %s\n'
                                ')\n'
                                'add_library(%s.completion STATIC EXCLUDE_FROM_ALL\n'
                                '    ${%s_SOURCES}\n'
                                ')\n' % (tg.name, '\n    '.join(files), tg.name, tg.name)
                            )
                        else:
                            CMakeLists.write(
                                'if(%s_SOURCES)\n'
                                'add_library(%s.completion STATIC EXCLUDE_FROM_ALL\n'
                                '    ${%s_SOURCES}\n'
                                ')\n' % (tg.name, tg.name, tg.name)
                            )

                        tg_includes = []
                        tg_includes += getattr(tg, 'includes', [])
                        tg_includes += getattr(tg, 'export_includes', [])
                        tg_includes += getattr(tg, 'export_system_includes', [])
                        tg_includes += getattr(tg, 'extra_includes', [])
                        tg_includes = [clion_path_from(i, self.srcnode) for i in tg_includes]

                        if tg_includes + tg.env.INCPATHS:
                            CMakeLists.write(
                                'target_include_directories(\n'
                                '    %s.completion\n'
                                '    PRIVATE\n'
                                '        "%s"\n'
                                ')\n\n' % (
                                    tg.name,
                                    '"\n        "'.join(tg_includes + [i.replace('\\', '/') for i in tg.env.INCPATHS])
                                )
                            )

                        tg_defines = []
                        tg_defines += getattr(tg, 'defines', [])
                        tg_defines += getattr(tg, 'export_defines', [])
                        tg_defines += getattr(tg, 'extra_defines', [])
                        tg_defines += tg.env.DEFINES
                        if tg_defines:
                            defines = (d.replace('(', '\\(').replace(')', '\\)') for d in tg_defines)
                            CMakeLists.write(
                                'target_compile_definitions(\n'
                                '    %s.completion\n'
                                '    PRIVATE\n'
                                '        %s\n'
                                ')\n\n' % (tg.name, '\n        '.join(defines))
                            )
                        if not files:
                            CMakeLists.write('endif()\n')

                        with open(
                                run_configs_dir.make_node('%s.completion.xml' % tg.name).path_from(self.path), 'w'
                        ) as run_file:
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
                        with open(run_configs_dir.make_node('%s.xml' % tg.name).path_from(self.path), 'w') as run_file:
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
            bld_env = self.all_envs[env_name]
            if bld_env.SUB_TOOLCHAINS:
                env = self.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env
            for variant in self.env.ALL_VARIANTS:
                dir_node = self.bldnode.make_node(env_name).make_node(variant)
                dir_node.mkdir()
                with open(dir_node.make_node('main.cpp').abspath(), 'w') as main_cpp:
                    pass
                with open(dir_node.make_node('CMakeLists.txt').abspath(), 'w') as CMakeLists:
                    CMakeLists.write('if (${CMAKE_BUILD_TYPE} STREQUAL %s-%s)\n\n' % (env_name, variant))
                    CMakeLists.write('set(CMAKE_CXX_FLAGS -std=c++14)\n')
                    CMakeLists.write('set(CMAKE_CXX_FLAGS --target=%s-generic)\n' % (env.ARCHITECTURE))
                    CMakeLists.write('set(WAF_COMMAND %s:%s)\n' % (env_name, variant))

                    for g in self.groups:
                        for tg in g:
                            if not isinstance(tg, TaskGen.task_gen):
                                continue

                            files = []
                            tg_special_files = special_files[tg]
                            for file in tg_special_files:
                                is_valid, _ = tg.apply_source_filter(env, file)
                                if is_valid:
                                    files.append(file.path_from(self.path).replace('\\', '/'))

                            if files:
                                CMakeLists.write(
                                    'list(APPEND %s_SOURCES\n'
                                    '    %s\n'
                                    ')\n' % (tg.name, '\n    '.join(files))
                                )

                    CMakeLists.write(
                        '\n'
                        'add_executable(%s %s)\n'
                        'set_property(TARGET %s PROPERTY\n'
                        '        RUNTIME_OUTPUT_DIRECTORY "../../../../../../%s/%s/%s/")\n'
                        'add_custom_command(TARGET %s POST_BUILD\n'
                        '    COMMAND "%s" "%s" build:%s:%s\n'
                        '    WORKING_DIRECTORY "%s"\n'
                        '    USES_TERMINAL\n'
                        ')\n\n'
                        'add_custom_target(prepare COMMAND cmake -E touch_nocreate main.cpp)\n'
                        'add_dependencies(motor.launcher prepare)\n'
                        'endif()\n' % (
                            self.launcher.target, dir_node.make_node('main.cpp').path_from(
                                self.path
                            ).replace('\\', '/'), self.launcher.target, bld_env.PREFIX.replace('\\', '/'), variant,
                            bld_env.DEPLOY_BINDIR.replace('\\', '/'), self.launcher.target,
                            sys.executable.replace('\\', '/'), sys.argv[0].replace('\\', '/'), env_name, variant,
                            self.srcnode.abspath().replace('\\', '/')
                        )
                    )

        for env_name in self.env.ALL_TOOLCHAINS:
            for variant in self.env.ALL_VARIANTS:
                for arg in ['', 'nomaster', 'static', 'dynamic']:
                    build_filename = run_configs_dir.make_node('build_%s_%s%s.xml' % (env_name, variant, arg)).abspath()
                    with open(build_filename, 'w') as run_config:
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
                            '    <option name="PARAMETERS" value="build:%(toolchain)s:%(variant)s %(arg)s" />\n'
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
                with open(
                        run_configs_dir.make_node('clean_%s_%s.xml' % (env_name, variant)).abspath(), 'w'
                ) as run_config:
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
        with open(run_configs_dir.make_node('clion.xml').abspath(), 'w') as run_config:
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
        with open(run_configs_dir.make_node('reconfigure.xml').abspath(), 'w') as run_config:
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
