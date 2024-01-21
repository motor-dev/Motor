import sys
import build_framework
import waflib.Node
import waflib.Task
import waflib.TaskGen
from typing import Dict, List, Optional, Tuple


class cmake_project(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        bld_env = self.generator.bld.all_envs[getattr(self, 'toolchain')]
        if bld_env.SUB_TOOLCHAINS:
            env = self.generator.bld.all_envs[bld_env.SUB_TOOLCHAINS[0]]
        else:
            env = bld_env
        self.m.update(getattr(self.generator.bld, 'launcher').target.encode())
        self.m.update(env.cxxprogram_PATTERN.encode())
        self.m.update(bld_env.PREFIX.encode())
        self.m.update(bld_env.DEPLOY_BINDIR.encode())
        self.m.update(sys.executable.encode())
        self.m.update(sys.argv[0].encode())
        self.m.update(str(getattr(self, 'main')).encode())

    def run(self) -> Optional[int]:
        with open(self.outputs[0].abspath(), 'w') as project:
            main = getattr(self, 'main')  # type: waflib.Node.Node
            toolchain = getattr(self, 'toolchain')  # type: str
            target = getattr(self.generator.bld, 'launcher').target
            bld_env = self.generator.bld.all_envs[toolchain]
            if bld_env.SUB_TOOLCHAINS:
                env = self.generator.bld.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env

            project.write(
                'add_compile_definitions(\n'
                '    %s\n'
                ')\n'
                'add_executable(%s %s)\n'
                'set_target_properties(%s PROPERTIES\n'
                '        RUNTIME_OUTPUT_NAME "%s"\n'
                '        RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/%s/${CMAKE_BUILD_TYPE}/%s"\n'
                '        ADDITIONAL_CLEAN_FILES "%s/%s.${CMAKE_BUILD_TYPE}"\n'
                ')\n'
                'add_custom_command(TARGET %s POST_BUILD\n'
                '    COMMAND "%s" "%s" build:%s:${CMAKE_BUILD_TYPE} --werror\n'
                '    WORKING_DIRECTORY "%s"\n'
                '    USES_TERMINAL\n'
                ')\n\n'
                'add_custom_target(prepare COMMAND ${CMAKE_COMMAND} -E touch_nocreate %s)\n'
                'set_target_properties(prepare PROPERTIES FOLDER completion/)\n'
                'add_dependencies(motor.launcher prepare)\n' % (
                    '\n    '.join(env.DEFINES),
                    target,
                    main.path_from(self.generator.bld.srcnode).replace('\\', '/'),
                    target,
                    env.cxxprogram_PATTERN % target,
                    bld_env.PREFIX.replace('\\', '/'),
                    env.DEPLOY_BINDIR.replace('\\', '/'),
                    self.generator.bld.bldnode.abspath().replace('\\', '/'),
                    toolchain,
                    target,
                    sys.executable.replace('\\', '/'),
                    sys.argv[0].replace('\\', '/'),
                    toolchain,
                    self.generator.bld.srcnode.abspath().replace('\\', '/'),
                    main.path_from(self.generator.bld.srcnode).replace('\\', '/'),
                )
            )
        return 0


class cmake_toolchain(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        env_name = getattr(self, 'toolchain')  # type: str
        env = self.generator.bld.all_envs[env_name]
        if env.SUB_TOOLCHAINS:
            arch_env = self.generator.bld.all_envs[env.SUB_TOOLCHAINS[0]]
        else:
            arch_env = env
        for value in (
                env.CC[0], env.CXX[0], arch_env.ARCHITECTURE, env.SYSTEM_NAME, ' '.join(env.COMPILER_C_FLAGS),
                ' '.join(env.COMPILER_CXX_FLAGS), ';'.join(env.COMPILER_C_DEFINES + env.COMPILER_CXX_DEFINES),
                ';'.join(env.COMPILER_C_INCLUDES + env.COMPILER_CXX_INCLUDES)
        ):
            self.m.update(value.encode())

    def run(self) -> Optional[int]:
        env_name = getattr(self, 'toolchain')  # type: str
        env = self.generator.bld.all_envs[env_name]
        if env.SUB_TOOLCHAINS:
            arch_env = self.generator.bld.all_envs[env.SUB_TOOLCHAINS[0]]
        else:
            arch_env = env
        with open(self.outputs[0].abspath(), 'w') as toolchain:
            toolchain.write(
                'set(CMAKE_CONFIGURATION_TYPES "%(configs)s" CACHE STRING "" FORCE)\n'
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
                '  message(STATUS "Using CMake compiler info")\n'
                '  add_compile_definitions("%(COMPILER_DEFINES)s")\n'
                '  include_directories("%(COMPILER_INCLUDES)s")\n'
                'endif()\n'
                '' % {
                    'configs':
                        ';'.join(self.generator.bld.env.ALL_VARIANTS),
                    'CC':
                        env.CC[0].replace('\\', '/'),
                    'CXX':
                        env.CXX[0].replace('\\', '/'),
                    'ENV':
                        env_name,
                    'ARCH':
                        arch_env.ARCHITECTURE,
                    'SYSTEM':
                        env.SYSTEM_NAME,
                    'COMPILER_C_FLAGS':
                        ' '.join(env.COMPILER_C_FLAGS),
                    'COMPILER_CXX_FLAGS':
                        ' '.join(env.COMPILER_CXX_FLAGS),
                    'COMPILER_DEFINES':
                        ';'.join(d.replace('"', '\\"') for d in env.COMPILER_C_DEFINES + env.COMPILER_CXX_DEFINES),
                    'COMPILER_INCLUDES':
                        ';'.join(i.replace('\\', '/') for i in env.COMPILER_C_INCLUDES + env.COMPILER_CXX_INCLUDES)
                }
            )

        return 0


@build_framework.autosig_generator('includes')
class cmake(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)
        self.m.update(sys.executable.encode())
        self.m.update(appname.encode())

    def run(self) -> Optional[int]:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)
        with open(self.outputs[0].abspath(), 'w') as main_cc:
            pass
        cmake_dir = self.outputs[1].parent.path_from(self.generator.bld.srcnode).replace('\\', '/')
        with open(self.outputs[1].abspath(), 'w') as project:
            for file in getattr(self.generator, 'includes'):
                project.write('include(%s)\n' % (file.path_from(self.generator.bld.srcnode).replace('\\', '/')))
            project.write('include(%s/${MOTOR_TOOLCHAIN}/targets.txt)\n' % cmake_dir)

        with open(self.outputs[2].abspath(), 'w') as root:
            root.write(
                'cmake_minimum_required(VERSION 3.15)\n'
                'project(%s)\n'
                'include(%s)' % (appname, self.outputs[3].path_from(self.generator.bld.srcnode).replace('\\', '/'))
            )
        with open(self.outputs[3].abspath(), 'w') as CMakeLists:
            CMakeLists.write(
                'set(CMAKE_C_COMPILER "%(python)s")\n'
                'set(CMAKE_CXX_COMPILER "%(python)s")\n'
                'set(CMAKE_C_COMPILER_ARG1 "%(true)s")\n'
                'set(CMAKE_CXX_COMPILER_ARG1 "%(true)s")\n'
                'set(CMAKE_C_LINKER_LAUNCHER "%(python)s;%(true)s;--")\n'
                'set(CMAKE_CXX_LINKER_LAUNCHER "%(python)s;%(true)s;--")\n'
                'set(CMAKE_CXX_STANDARD 14)\n'
                'set(CMAKE_CXX_STANDARD_REQUIRED ON)\n'
                'set(CMAKE_CXX_EXTENSIONS OFF)\n'
                'set_property(GLOBAL PROPERTY TARGET_MESSAGES OFF)\n'
                'set_property(GLOBAL PROPERTY RULE_MESSAGES OFF)\n'
                'set_property(GLOBAL PROPERTY USE_FOLDERS ON)\n'
                'message(STATUS "Using toolchain file: ${CMAKE_TOOLCHAIN_FILE}")\n'
                'include(%(cmake_dir)s/project.txt)\n'
                '' % {
                    'cmake_dir':
                        cmake_dir,
                    'python':
                        sys.executable.replace('\\', '/'),
                    'true':
                        getattr(self.generator.bld,
                                'motornode').make_node('mak/bin/true.py').abspath().replace('\\', '/')
                }
            )

        return 0


@build_framework.autosig_vars('defines', 'include_nodes', 'all_nodes', 'source_nodes', 'variant_nodes')
class cmakelists(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> Optional[int]:
        all_nodes = getattr(self, 'all_nodes')  # type: List[Tuple[str, waflib.Node.Node, List[waflib.Node.Node]]]
        source_nodes = getattr(self, 'source_nodes')  # type: List[waflib.Node.Node]
        variant_nodes = getattr(self, 'variant_nodes')  # type:  Dict[waflib.Node.Node, List[str]]
        defines = getattr(self, 'defines')  # type: List[str]
        include_nodes = getattr(self, 'include_nodes')  # type: List[waflib.Node.Node]
        motor_target = getattr(self, 'motor_target')  # type: str

        with open(self.outputs[0].abspath(), 'w') as cmakelists:
            cmakelists.write(
                'add_library(%s.completion STATIC EXCLUDE_FROM_ALL\n'
                '    ${PROJECT_SOURCE_DIR}/%s\n'
                ')\n'
                'set_target_properties(%s.completion PROPERTIES LINKER_LANGUAGE CXX)\n'
                'set_target_properties(%s.completion PROPERTIES FOLDER completion/%s)\n'
                '' % (
                    motor_target,
                    '\n    ${PROJECT_SOURCE_DIR}/'.join(
                        [f.path_from(self.generator.bld.srcnode).replace('\\', '/') for _, _, file_list in all_nodes for
                         f in file_list]
                    ),
                    motor_target,
                    motor_target,
                    '/'.join(motor_target.split('.')[:-1]),
                )
            )
            if include_nodes:
                cmakelists.write(
                    'target_include_directories(%s.completion PRIVATE\n'
                    '    %s\n'
                    ')\n' % (motor_target, '\n    '.join([str(i).replace('\\', '/') for i in include_nodes]))
                )
            if defines:
                cmakelists.write(
                    'target_compile_definitions(%s.completion PRIVATE\n'
                    '    "%s"\n'
                    ')\n' % (motor_target, '"\n    "'.join([d.replace('"', '\\"') for d in defines]))
                )
            for prefix, source_node, nodes in all_nodes:
                cmakelists.write(
                    'source_group(TREE ${PROJECT_SOURCE_DIR}/%s PREFIX "%s" FILES\n'
                    '    ${PROJECT_SOURCE_DIR}/%s\n'
                    ')\n' % (
                        source_node.path_from(self.generator.bld.srcnode).replace('\\', '/'), prefix,
                        '\n    ${PROJECT_SOURCE_DIR}/'.join(
                            [node.path_from(self.generator.bld.srcnode).replace('\\', '/') for node in nodes]
                        )
                    )
                )

            cl_files = []
            for file in source_nodes:
                if file.name.endswith('.cl'):
                    cl_files.append(file)
            if cl_files:
                cmakelists.write(
                    'set_source_files_properties(\n'
                    '    ${PROJECT_SOURCE_DIR}/%s\n'
                    '    PROPERTIES\n'
                    '        LANGUAGE CXX\n'
                    ')\n' % '\n    ${PROJECT_SOURCE_DIR}/'.join(
                        [node.path_from(self.generator.bld.srcnode).replace('\\', '/') for node in cl_files]
                    )
                )

            non_source_nodes = []
            for _, _, file_list in all_nodes:
                non_source_nodes += [
                    node for node in file_list if node not in source_nodes and node not in variant_nodes
                ]
            if non_source_nodes:
                cmakelists.write(
                    'set_source_files_properties(\n'
                    '    ${PROJECT_SOURCE_DIR}/%s\n'
                    '    PROPERTIES\n'
                    '        HEADER_FILE_ONLY ON\n'
                    '        LANGUAGE Disabled\n'
                    ')\n' % '\n    ${PROJECT_SOURCE_DIR}/'.join(
                        [node.path_from(self.generator.bld.srcnode).replace('\\', '/') for node in non_source_nodes]
                    )
                )
            for variant in self.generator.bld.env.ALL_TOOLCHAINS:
                disabled_nodes = []
                for node, variants in variant_nodes.items():
                    if variant not in variants:
                        disabled_nodes.append(node)
                if disabled_nodes:
                    cmakelists.write(
                        'if (${MOTOR_TOOLCHAIN} STREQUAL %s)\n'
                        '    set_source_files_properties(\n'
                        '        ${PROJECT_SOURCE_DIR}/%s\n'
                        '        PROPERTIES\n'
                        '            HEADER_FILE_ONLY ON\n'
                        '            LANGUAGE Disabled\n'
                        '    )\n'
                        'endif()\n' % (
                            variant, '\n        ${PROJECT_SOURCE_DIR}/'.join(
                                [
                                    node.path_from(self.generator.bld.srcnode).replace('\\', '/')
                                    for node in disabled_nodes
                                ]
                            )
                        )
                    )
        return 0


@waflib.TaskGen.feature('motor:cmake')
def process_cmake(task_gen: waflib.TaskGen.task_gen) -> None:
    cmake_dir = task_gen.bld.bldnode.make_node(getattr(task_gen, 'group'))
    main_cc = cmake_dir.make_node('main.cc')
    for toolchain in task_gen.env.ALL_TOOLCHAINS:
        toolchain_dir = cmake_dir.make_node(toolchain)
        toolchain_dir.mkdir()
        toolchain_file = toolchain_dir.make_node('toolchain.txt')
        task_gen.create_task(
            'cmake_toolchain',
            [],
            [toolchain_dir.make_node('toolchain.txt')],
            toolchain=toolchain,
        )
        task_gen.create_task(
            'cmake_project', [], [toolchain_dir.make_node('targets.txt')], toolchain=toolchain, main=main_cc
        )
        getattr(task_gen, 'toolchains').append((toolchain, toolchain_file))
    appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, task_gen.bld.srcnode.name)
    task_gen.create_task(
        'cmake',
        [],
        [
            main_cc,
            cmake_dir.make_node('project.txt'),
            task_gen.bld.srcnode.make_node('CMakeLists.txt'),
            task_gen.bld.srcnode.make_node('%s.cmake' % appname),
        ],
    )


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
@waflib.TaskGen.after_method('propagate_uselib_vars')
@waflib.TaskGen.after_method('apply_incpaths')
@waflib.TaskGen.after_method('install_step')
def create_cmakelists(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'cmake' in task_gen.env.PROJECTS:
        all_nodes = []  # type: List[Tuple[str, waflib.Node.Node, List[waflib.Node.Node]]]
        source_nodes = []  # type: List[waflib.Node.Node]
        variant_nodes = {}  # type: Dict[waflib.Node.Node, List[str]]

        root_nodes = getattr(task_gen, 'source_nodes')  # type: List[Tuple[str, waflib.Node.Node]]
        for name, root_node in root_nodes:
            if root_node.isdir():
                all_sub_nodes = root_node.ant_glob('**/*', excl=['kernels/**', 'tests/**', '**/*.pyc'], remove=False)
                all_nodes.append((name, root_node, all_sub_nodes))
            else:
                all_sub_nodes = [root_node]
                all_nodes.append((name, root_node.parent, all_sub_nodes))

        for task in task_gen.tasks:
            if task.__class__.__name__ in ('c', 'objc', 'cxx', 'objcxx', 'cpuc'):
                node = task.inputs[0]

                _, filter = build_framework.apply_source_filter(task_gen, task_gen.bld.env, node)
                if not filter:
                    source_nodes.append(node)
                else:
                    for variant in task_gen.env.ALL_TOOLCHAINS:
                        env = task_gen.bld.all_envs[variant]
                        if build_framework.apply_source_filter(task_gen, env, node)[0]:
                            try:
                                variant_nodes[node].append(variant)
                            except KeyError:
                                variant_nodes[node] = [variant]

        motor_cmake_tg = getattr(task_gen.bld, 'motor_cmake_tg')  # type: waflib.TaskGen.task_gen
        cmake_dir = task_gen.bld.bldnode.make_node(getattr(motor_cmake_tg, 'group'))
        cmake_dir.mkdir()
        lists_node = cmake_dir.make_node('%s.txt' % task_gen.target)
        motor_cmake_tg.create_task(
            'cmakelists', [], [lists_node],
            motor_target=task_gen.target,
            include_nodes=getattr(task_gen, 'includes_nodes'),
            defines=task_gen.env.DEFINES,
            all_nodes=all_nodes,
            source_nodes=source_nodes,
            variant_nodes=variant_nodes
        )
        getattr(motor_cmake_tg, 'includes').append(lists_node)


def build(build_context: build_framework.BuildContext) -> None:
    if 'cmake' in build_context.env.PROJECTS:
        motor_cmake_tg = build_context(
            group='cmake', features=['motor:cmake'], target='cmake', includes=[], toolchains=[]
        )
        setattr(build_context, 'motor_cmake_tg', motor_cmake_tg)
