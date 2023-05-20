import os.path
import sys

from waflib import Context, Build, TaskGen, Options


def cmake_path_from(path, node):
    if isinstance(path, str):
        return path.replace('\\', '/')
    else:
        return path.path_from(node).replace('\\', '/')


def get_define(d):
    value_pos = d.find('=') + 1
    if value_pos:
        return '%s: %s' % (d[:value_pos - 1], d[value_pos:].replace('"', '\\"'))
    else:
        return '%s:' % d


def write_cmake_workspace(build_context, build_options=[]):
    appname = getattr(Context.g_module, Context.APPNAME, build_context.srcnode.name)

    files = []
    bld_path = build_context.bldnode.path_from(build_context.srcnode).replace('\\', '/')
    cmake_dir = build_context.bldnode.parent.make_node('cmake')
    cmake_dir.mkdir()
    configurations = []

    for env_name in build_context.env.ALL_TOOLCHAINS:
        bld_env = build_context.all_envs[env_name]
        if bld_env.SUB_TOOLCHAINS:
            env = build_context.all_envs[bld_env.SUB_TOOLCHAINS[0]]
        else:
            env = bld_env
        toolchain_dir = cmake_dir.make_node(env_name)
        toolchain_dir.mkdir()
        toolchain = toolchain_dir.make_node('toolchain.txt').path_from(build_context.srcnode)
        configurations.append((env_name, toolchain))
        with open(toolchain, 'w') as toolchain_file:
            toolchain_file.write(
                'set(CMAKE_C_COMPILER %s CACHE STRING "")\n'
                'set(CMAKE_CXX_COMPILER %s  CACHE STRING "")\n'
                'set(MOTOR_TOOLCHAIN %s CACHE INTERNAL "" FORCE)\n'
                'set(triple %s-%s)\n'
                'set(CMAKE_SYSTEM_NAME Generic)\n'
                'set(CMAKE_C_COMPILER_WORKS TRUE)\n'
                'set(CMAKE_CXX_COMPILER_WORKS TRUE)\n'
                'set(CMAKE_C_FLAGS "-U%s --target=%s-%s %s")\n'
                'set(CMAKE_CXX_FLAGS "-U%s --target=%s-%s %s")\n'
                '' % (
                    env.CC[0], env.CXX[0], env_name, env.ARCHITECTURE, env.SYSTEM_NAME, env_name, env.ARCHITECTURE,
                    env.SYSTEM_NAME, ' '.join(env.COMPILER_C_FLAGS), env_name, env.ARCHITECTURE, env.SYSTEM_NAME,
                    ' '.join(env.COMPILER_CXX_FLAGS)
                )
            )

    with open(cmake_dir.make_node('project.txt').abspath(), 'w') as CMakeLists:
        special_files_tg = {}
        for g in build_context.groups:
            for tg in g:
                if not isinstance(tg, TaskGen.task_gen):
                    continue
                if 'motor:preprocess' in tg.features:
                    continue
                tg.post()

                tg_includes = [
                    i.replace('\\', '/') for i in tg.env.INCPATHS
                    if i not in env.INCLUDES + env.COMPILER_C_INCLUDES + env.COMPILER_CXX_INCLUDES
                ]
                tg_defines = []
                tg_defines += getattr(tg, 'defines', [])
                tg_defines += getattr(tg, 'export_defines', [])
                tg_defines += getattr(tg, 'extra_defines', [])
                tg_defines += tg.env.DEFINES
                special_files = {}
                special_files_tg[tg] = special_files
                files = {}
                all_files = {}

                tg_path = tg.name.replace('.', '/')
                for prefix, source_node in tg.source_nodes:
                    if source_node.isdir():
                        tg_files = source_node.ant_glob('**/*', excl='kernels/**')
                        if tg_files:
                            all_files[(tg_path + '/' + prefix, source_node)
                                      ] = [f.path_from(build_context.srcnode).replace('\\', '/') for f in tg_files]
                    else:
                        all_files[(tg_path + '/' + prefix, source_node.parent)
                                  ] = [source_node.path_from(build_context.srcnode).replace('\\', '/')]

                for task in tg.tasks:
                    if task.__class__.__name__ in ('c', 'objc', 'cxx', 'objcxx', 'cpuc'):
                        _, had_filter = tg.apply_source_filter(tg.env, task.inputs[0])
                        filename = task.inputs[0].path_from(build_context.srcnode).replace('\\', '/')
                        if not had_filter:
                            files[filename] = (tg_includes, tg_defines)
                        else:
                            special_files[filename] = task.inputs[0]
                if 'motor:kernel' in tg.features:
                    _, had_filter = tg.apply_source_filter(tg.env, tg.source[0])
                    filename = tg.source[0].path_from(build_context.srcnode).replace('\\', '/')
                    if not had_filter:
                        files[filename] = (tg_includes, tg_defines)
                    else:
                        special_files[filename] = tg.source[0]

                target_file = cmake_dir.make_node('%s.txt' % tg.name).path_from(build_context.srcnode)
                CMakeLists.write('include(%s)\n' % target_file)
                with open(target_file, 'w') as target_list:
                    if files or special_files:
                        target_list.write(
                            'add_library(%s.completion STATIC EXCLUDE_FROM_ALL\n'
                            '    ${CMAKE_CURRENT_SOURCE_DIR}/%s\n'
                            ')\n' % (
                                tg.target, '\n    ${CMAKE_CURRENT_SOURCE_DIR}/'.join(
                                    [
                                        f for _, file_list in all_files.items()
                                        for f in file_list if f not in special_files
                                    ]
                                )
                            )
                        )
                        if tg_includes:
                            target_list.write(
                                'target_include_directories(%s.completion PRIVATE\n'
                                '    %s\n'
                                ')\n' % (tg.target, '\n    '.join(tg_includes))
                            )
                        if tg_defines:
                            target_list.write(
                                'target_compile_definitions(%s.completion PRIVATE\n'
                                '    "%s"\n'
                                ')\n' % (tg.target, '"\n    "'.join(tg_defines))
                            )
                        disabled_files = []
                        for _, file_list in all_files.items():
                            for file in file_list:
                                if file in special_files:
                                    continue
                                if file not in files:
                                    disabled_files.append(file)
                        if disabled_files:
                            target_list.write(
                                'set_source_files_properties(\n'
                                '    ${CMAKE_CURRENT_SOURCE_DIR}/%s\n'
                                '    PROPERTY HEADER_FILE_ONLY ON\n'
                                '    PROPERTY LANGUAGE Disabled\n'
                                ')\n' % '\n    ${CMAKE_CURRENT_SOURCE_DIR}/'.join(disabled_files)
                            )
                    elif all_files:
                        target_list.write(
                            'add_library(%s.completion INTERFACE\n'
                            '    ${CMAKE_CURRENT_SOURCE_DIR}/%s\n'
                            ')\n' % (
                                tg.target, '\n    ${CMAKE_CURRENT_SOURCE_DIR}/'.join(
                                    [f for _, file_list in all_files.items() for f in file_list]
                                )
                            )
                        )
                    for (prefix, source_node), prefix_files in all_files.items():
                        source_path = source_node.path_from(build_context.srcnode).replace('\\', '/')
                        target_list.write(
                            'source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR}/%s PREFIX "" FILES\n'
                            '    ${CMAKE_CURRENT_SOURCE_DIR}/%s\n'
                            ')\n' % (source_path, '\n    ${CMAKE_CURRENT_SOURCE_DIR}/'.join(prefix_files))
                        )
                    if 'motor:kernel' in tg.features:
                        target_list.write(
                            'set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/%s PROPERTIES LANGUAGE CXX)\n' %
                            (tg.source[0].path_from(build_context.srcnode).replace('\\','/'))
                        )

        for env_name in build_context.env.ALL_TOOLCHAINS:
            bld_env = build_context.all_envs[env_name]
            if bld_env.SUB_TOOLCHAINS:
                env = build_context.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env
            target_file = cmake_dir.make_node(env_name).make_node('targets.txt')
            target_file.parent.mkdir()
            CMakeLists.write(
                'if (${MOTOR_TOOLCHAIN} STREQUAL %s)\n'
                '    include(%s)\n'
                'endif()\n'
                '' % (env_name, target_file.path_from(build_context.path))
            )
            with open(target_file.abspath(), 'w') as CMakeLists_variant:
                CMakeLists_variant.write(
                    'add_compile_definitions(\n'
                    '    %s\n'
                    ')\n'
                    '\n'
                    'add_executable(%s %s)\n'
                    'set_property(TARGET %s PROPERTY\n'
                    '        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/%s/${CMAKE_BUILD_TYPE}/%s/")\n'
                    'add_custom_command(TARGET %s POST_BUILD\n'
                    '    COMMAND "%s" "%s" build:%s:${CMAKE_BUILD_TYPE} %s\n'
                    '    WORKING_DIRECTORY "%s"\n'
                    '    USES_TERMINAL\n'
                    ')\n\n'
                    'add_custom_target(prepare COMMAND cmake -E touch_nocreate main.cpp)\n'
                    'add_dependencies(motor.launcher prepare)\n'
                    '' % (
                        '\n    '.join(env.DEFINES), build_context.launcher.target,
                        cmake_dir.make_node('main.cpp').path_from(build_context.path).replace('\\', '/'),
                        build_context.launcher.target, bld_env.PREFIX.replace('\\', '/'),
                        bld_env.DEPLOY_BINDIR.replace('\\', '/'), build_context.launcher.target,
                        sys.executable.replace('\\', '/'), sys.argv[0].replace('\\', '/'), env_name,
                        ' '.join(build_options), build_context.srcnode.abspath().replace('\\', '/')
                    )
                )
                for tg, file_list in special_files_tg.items():
                    platform_files = []
                    for file, file_node in file_list.items():
                        add, _ = tg.apply_source_filter(env, file_node)
                        if add:
                            platform_files.append(file)
                    if platform_files:
                        CMakeLists_variant.write(
                            'target_sources(\n'
                            '    %s.completion PRIVATE\n'
                            '    ${CMAKE_CURRENT_SOURCE_DIR}/%s\n'
                            ')\n' % (tg.name, '\n    ${CMAKE_CURRENT_SOURCE_DIR}/'.join(platform_files))
                        )
    with open(cmake_dir.make_node('main.cpp').abspath(), 'w') as main:
        pass
    with open('CMakeLists.txt', 'w') as CMakeLists:
        CMakeLists.write(
            'cmake_minimum_required(VERSION 3.15)\n'
            'set(CMAKE_C_COMPILER_LAUNCHER %(python)s %(true)s)\n'
            'set(CMAKE_CXX_COMPILER_LAUNCHER %(python)s %(true)s)\n'
            'set(CMAKE_C_LINKER_LAUNCHER %(python)s %(true)s)\n'
            'set(CMAKE_CXX_LINKER_LAUNCHER %(python)s %(true)s)\n'
            'project(%(appname)s)\n'
            'set(CMAKE_CONFIGURATION_TYPES "%(configs)s" CACHE STRING "" FORCE)\n\n'
            'set(CMAKE_CXX_STANDARD 14)\n'
            'set(CMAKE_CXX_STANDARD_REQUIRED ON)\n'
            'set(CMAKE_CXX_EXTENSIONS OFF)\n'
            'set_property(GLOBAL PROPERTY TARGET_MESSAGES OFF)\n'
            'set_property(GLOBAL PROPERTY RULE_MESSAGES OFF)\n'
            'MESSAGE(STATUS "Using toolchain file: ${CMAKE_TOOLCHAIN_FILE}")\n'
            'include(%(cmake_dir)s/project.txt)\n'
            '' % {
                'appname': appname,
                'configs': ';'.join(build_context.env.ALL_VARIANTS),
                'cmake_dir': cmake_dir.path_from(build_context.srcnode),
                'python': sys.executable,
                'true': build_context.motornode.make_node('mak/tools/bin/true.py').abspath()
            }
        )

    return configurations


class CMake(Build.BuildContext):
    """
        creates CMake project structure. Used by ither CMake-based project generators.
    """
    cmd = 'cmake'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/cmake'

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
        return self.write_workspace()

    def write_workspace(self):
        return write_cmake_workspace(self)
