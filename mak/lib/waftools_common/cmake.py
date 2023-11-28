import sys
import build_framework
import waflib.Context
import waflib.Node
import waflib.TaskGen
from typing import Any, Dict, List, Optional, Tuple


def write_cmake_workspace(
        build_context: build_framework.BuildContext,
        build_options: Optional[List[str]] = None
) -> List[Tuple[str, str]]:
    appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, build_context.srcnode.name)
    cmake_dir = build_context.bldnode.make_node('cmake')
    cmake_dir.mkdir()
    configurations = []

    for env_name in build_context.env.ALL_TOOLCHAINS:
        bld_env = build_context.all_envs[env_name]
        env = bld_env
        if bld_env.SUB_TOOLCHAINS:
            env = build_context.all_envs[bld_env.SUB_TOOLCHAINS[0]]
        toolchain_dir = cmake_dir.make_node(env_name)
        toolchain_dir.mkdir()
        toolchain = toolchain_dir.make_node('toolchain.txt').path_from(build_context.srcnode)
        configurations.append((env_name, toolchain))
        with open(toolchain, 'w') as toolchain_file:
            toolchain_file.write(
                'set(CMAKE_C_COMPILER "%(CC)s" CACHE STRING "")\n'
                'set(CMAKE_CXX_COMPILER "%(CXX)s"  CACHE STRING "")\n'
                'set(MOTOR_TOOLCHAIN %(ENV)s CACHE INTERNAL "" FORCE)\n'
                'set(triple %(ARCH)s-%(SYSTEM)s)\n'
                'set(CMAKE_SYSTEM_NAME Generic)\n'
                'set(CMAKE_C_COMPILER_WORKS TRUE)\n'
                'set(CMAKE_CXX_COMPILER_WORKS TRUE)\n'
                'set(CMAKE_C_FLAGS "-U%(ENV)s --target=%(ARCH)s-%(SYSTEM)s %(COMPILER_C_FLAGS)s")\n'
                'set(CMAKE_CXX_FLAGS "-U%(ENV)s --target=%(ARCH)s-%(SYSTEM)s %(COMPILER_CXX_FLAGS)s")\n'
                'if(USE_CMAKE_COMPILER_INFORMATION)\n'
                '  add_compile_definitions("%(COMPILER_DEFINES)s")\n'
                '  include_directories("%(COMPILER_INCLUDES)s")\n'
                'endif()\n'
                '' % {
                    'CC': env.CC[0].replace('\\', '/'),
                    'CXX': env.CXX[0].replace('\\', '/'),
                    'ENV': env_name,
                    'ARCH': env.ARCHITECTURE,
                    'SYSTEM': env.SYSTEM_NAME,
                    'COMPILER_C_FLAGS': ' '.join(env.COMPILER_C_FLAGS),
                    'COMPILER_CXX_FLAGS': ' '.join(env.COMPILER_CXX_FLAGS),
                    'COMPILER_DEFINES': ';'.join(
                        d.replace('"', '\\"') for d in env.COMPILER_C_DEFINES + env.COMPILER_CXX_DEFINES),
                    'COMPILER_INCLUDES': ';'.join(
                        i.replace('\\', '/') for i in env.COMPILER_C_INCLUDES + env.COMPILER_CXX_INCLUDES)
                }
            )
    with open(cmake_dir.make_node('project.txt').abspath(), 'w') as CMakeLists:
        special_files_tg = {}
        for g in build_context.groups:
            for tg in g:
                env = tg.env
                if not isinstance(tg, waflib.TaskGen.task_gen):
                    continue
                if 'motor:preprocess' in tg.features:
                    continue
                tg.post()

                tg_includes = [
                    i.replace('\\', '/') for i in tg.env.INCPATHS
                    if i not in env.INCLUDES + env.COMPILER_C_INCLUDES + env.COMPILER_CXX_INCLUDES
                ]
                tg_defines = []  # type: List[str]
                tg_defines += getattr(tg, 'defines', [])
                tg_defines += getattr(tg, 'export_defines', [])
                tg_defines += getattr(tg, 'extra_defines', [])
                tg_defines += tg.env.DEFINES
                special_files = {}  # type: Dict[str, waflib.Node.Node]
                special_files_tg[tg] = special_files
                files = {}
                all_files = {}

                tg_path = tg.name.replace('.', '/')
                for prefix, source_node in getattr(tg, 'source_nodes'):
                    if source_node.isdir():
                        tg_files = source_node.ant_glob('**/*', excl=['kernels/**', '**/*.pyc'])
                        if tg_files:
                            all_files[(tg_path + '/' + prefix, source_node)] = [
                                f.path_from(build_context.srcnode).replace('\\', '/') for f in tg_files]
                    else:
                        all_files[(tg_path + '/' + prefix, source_node.parent)] = [
                            source_node.path_from(build_context.srcnode).replace('\\', '/')]

                for task in tg.tasks:
                    if task.__class__.__name__ in ('c', 'objc', 'cxx', 'objcxx', 'cpuc'):
                        _, had_filter = build_framework.apply_source_filter(tg, tg.env, task.inputs[0])
                        filename = task.inputs[0].path_from(build_context.srcnode).replace('\\', '/')
                        if not had_filter:
                            files[filename] = (tg_includes, tg_defines)
                        else:
                            special_files[filename] = task.inputs[0]
                if 'motor:kernel' in tg.features:
                    _, had_filter = build_framework.apply_source_filter(tg, tg.env, tg.source[0])
                    filename = tg.source[0].path_from(build_context.srcnode).replace('\\', '/')
                    if not had_filter:
                        files[filename] = (tg_includes, tg_defines)
                    else:
                        special_files[filename] = tg.source[0]

                target_file = cmake_dir.make_node('%s.txt' % tg.name).path_from(build_context.srcnode)
                CMakeLists.write('include(%s)\n' % target_file.replace('\\', '/'))
                with open(target_file, 'w') as target_list:
                    if files or special_files:
                        target_list.write(
                            'add_library(%s.completion STATIC EXCLUDE_FROM_ALL\n'
                            '    ${PROJECT_SOURCE_DIR}/%s\n'
                            ')\n' % (
                                tg.target, '\n    ${PROJECT_SOURCE_DIR}/'.join(
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
                                '    ${PROJECT_SOURCE_DIR}/%s\n'
                                '    PROPERTY HEADER_FILE_ONLY ON\n'
                                '    PROPERTY LANGUAGE Disabled\n'
                                ')\n' % '\n    ${PROJECT_SOURCE_DIR}/'.join(disabled_files)
                            )
                    elif all_files:
                        target_list.write(
                            'add_library(%s.completion INTERFACE\n'
                            '    ${PROJECT_SOURCE_DIR}/%s\n'
                            ')\n' % (
                                tg.target, '\n    ${PROJECT_SOURCE_DIR}/'.join(
                                    [f for _, file_list in all_files.items() for f in file_list]
                                )
                            )
                        )
                    for (prefix, source_node), prefix_files in all_files.items():
                        source_path = source_node.path_from(build_context.srcnode).replace('\\', '/')
                        target_list.write(
                            'source_group(TREE ${PROJECT_SOURCE_DIR}/%s PREFIX "" FILES\n'
                            '    ${PROJECT_SOURCE_DIR}/%s\n'
                            ')\n' % (source_path, '\n    ${PROJECT_SOURCE_DIR}/'.join(prefix_files))
                        )
                    if 'motor:kernel' in tg.features:
                        target_list.write(
                            'set_source_files_properties(${PROJECT_SOURCE_DIR}/%s PROPERTIES LANGUAGE CXX)\n' %
                            (tg.source[0].path_from(build_context.srcnode).replace('\\', '/'))
                        )

        CMakeLists.write(
            'include(%s/${MOTOR_TOOLCHAIN}/targets.txt)\n'
            '' % (cmake_dir.path_from(build_context.path).replace('\\', '/'))
        )
        for env_name in build_context.env.ALL_TOOLCHAINS:
            bld_env = build_context.all_envs[env_name]
            if bld_env.SUB_TOOLCHAINS:
                env = build_context.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env
            target_node = cmake_dir.make_node(env_name).make_node('targets.txt')
            target_node.parent.mkdir()
            with open(target_node.abspath(), 'w') as CMakeLists_variant:
                assert build_context.launcher is not None
                CMakeLists_variant.write(
                    'add_compile_definitions(\n'
                    '    %s\n'
                    ')\n'
                    '\n'
                    'add_executable(%s %s)\n'
                    'set_target_properties(%s PROPERTIES\n'
                    '        RUNTIME_OUTPUT_NAME "%s"\n'
                    '        RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/%s/${CMAKE_BUILD_TYPE}/%s")\n'
                    'add_custom_command(TARGET %s POST_BUILD\n'
                    '    COMMAND "%s" "%s" build:%s:${CMAKE_BUILD_TYPE} --werror %s\n'
                    '    WORKING_DIRECTORY "%s"\n'
                    '    USES_TERMINAL\n'
                    ')\n\n'
                    'add_custom_target(prepare COMMAND ${CMAKE_COMMAND} -E touch_nocreate main.cpp)\n'
                    'add_dependencies(motor.launcher prepare)\n'
                    '' % (
                        '\n    '.join(env.DEFINES),
                        build_context.launcher.target,
                        cmake_dir.make_node('main.cpp').path_from(build_context.path).replace('\\', '/'),
                        build_context.launcher.target,
                        env.cxxprogram_PATTERN % build_context.launcher.target,
                        bld_env.PREFIX.replace('\\', '/'),
                        env.DEPLOY_BINDIR.replace('\\', '/'), build_context.launcher.target,
                        sys.executable.replace('\\', '/'), sys.argv[0].replace('\\', '/'), env_name,
                        ' '.join(build_options or []), build_context.srcnode.abspath().replace('\\', '/')
                    )
                )
                for tg, tg_file_list in special_files_tg.items():
                    platform_files = []
                    for file, file_node in tg_file_list.items():
                        add, _ = build_framework.apply_source_filter(tg, env, file_node)
                        if add:
                            platform_files.append(file)
                    if platform_files:
                        CMakeLists_variant.write(
                            'target_sources(\n'
                            '    %s.completion PRIVATE\n'
                            '    ${PROJECT_SOURCE_DIR}/%s\n'
                            ')\n' % (tg.name, '\n    ${PROJECT_SOURCE_DIR}/'.join(platform_files))
                        )
    with open(cmake_dir.make_node('main.cpp').abspath(), 'w'):
        pass

    with open('CMakeLists.txt', 'w') as CMakeLists:
        CMakeLists.write('cmake_minimum_required(VERSION 3.15)\n'
                         'project(%s)\n'
                         'include(%s.cmake)' % (appname, appname))

    with open('%s.cmake' % appname, 'w') as CMakeLists:
        CMakeLists.write(
            'set(CMAKE_C_COMPILER "%(python)s")\n'
            'set(CMAKE_CXX_COMPILER "%(python)s")\n'
            'set(CMAKE_C_COMPILER_ARG1 "%(true)s")\n'
            'set(CMAKE_CXX_COMPILER_ARG1 "%(true)s")\n'
            'set(CMAKE_C_LINKER_LAUNCHER "%(python)s;%(true)s;--")\n'
            'set(CMAKE_CXX_LINKER_LAUNCHER "%(python)s;%(true)s;--")\n'
            'set(CMAKE_CONFIGURATION_TYPES "%(configs)s" CACHE STRING "" FORCE)\n\n'
            'set(CMAKE_CXX_STANDARD 14)\n'
            'set(CMAKE_CXX_STANDARD_REQUIRED ON)\n'
            'set(CMAKE_CXX_EXTENSIONS OFF)\n'
            'set_property(GLOBAL PROPERTY TARGET_MESSAGES OFF)\n'
            'set_property(GLOBAL PROPERTY RULE_MESSAGES OFF)\n'
            'MESSAGE(STATUS "Using toolchain file: ${CMAKE_TOOLCHAIN_FILE}")\n'
            'include(%(cmake_dir)s/project.txt)\n'
            '' % {
                'configs': ';'.join(build_context.env.ALL_VARIANTS),
                'cmake_dir': cmake_dir.path_from(build_context.srcnode).replace('\\', '/'),
                'python': sys.executable.replace('\\', '\\\\'),
                'true': build_context.motornode.make_node('mak/bin/true.py').abspath().replace('\\', '\\\\')
            }
        )

    return configurations