import os
import re

import build_framework
import waflib.Build
import waflib.ConfigSet
import waflib.Errors
import waflib.Logs
import waflib.Node
import waflib.Options
import waflib.Task
import waflib.TaskGen
import waflib.Utils
import waflib.Tools.ccroot

from typing import Optional, Tuple, Union

waflib.Build.PROTOCOL = 2

waflib.Tools.ccroot.USELIB_VARS['cxx'].add('CLC_CXXFLAGS')
waflib.Tools.ccroot.USELIB_VARS['cxx'].add('SYSTEM_INCLUDES')


def _safe_target_name(target: str) -> str:
    return re.sub('_+', '_', re.sub('[^a-zA-Z0-9_]*', '_', target.split('.')[-1]))


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
def set_optim_define(task_gen: waflib.TaskGen.task_gen) -> None:
    o = getattr(task_gen.bld, 'optim', None)
    if o:
        task_gen.env.append_unique('DEFINES', ['MOTOR_%s' % o.upper()])


@waflib.TaskGen.feature('motor:cxx')
def set_building_name_inherits(task_gen: waflib.TaskGen.task_gen) -> None:
    seen = set([])
    use = getattr(task_gen, 'use', [])[:]
    while use:
        x = use.pop()
        if x in seen:
            continue
        seen.add(x)
        try:
            y = task_gen.bld.get_tgen_by_name(x)
        except waflib.Errors.WafError:
            pass
        else:
            if 'cxxobjects' in y.features:
                use += getattr(y, 'use', [])
                task_gen.env.append_unique('DEFINES', 'building_%s' % _safe_target_name(y.target))


@waflib.TaskGen.feature('motor:launcher', 'motor:unit_test', 'motor:python_module')
@waflib.TaskGen.before_method('apply_link')
@waflib.TaskGen.before_method('process_use')
def static_dependencies(task_gen: waflib.TaskGen.task_gen) -> None:
    if task_gen.bld.env.STATIC:
        for g in task_gen.bld.groups:
            for dependency in g:
                if not isinstance(dependency, waflib.TaskGen.task_gen):
                    continue
                if (
                        'motor:kernel' in dependency.features or 'motor:plugin' in dependency.features
                ) and 'cxx' in dependency.features:
                    dependency.post()
                    if dependency.env.TOOLCHAIN == task_gen.env.TOOLCHAIN:
                        getattr(task_gen, 'use').append(dependency.target)


@waflib.TaskGen.feature('motor:launcher_static')
@waflib.TaskGen.before_method('apply_link')
def rename_executable(task_gen: waflib.TaskGen.task_gen) -> None:
    task_gen.target = getattr(task_gen, 'real_target', task_gen.target)


@waflib.TaskGen.feature('cxxobjects')
def objects_feature(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('Makefile')
def makefile_feature(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('motor:warnings:off', 'motor:nortc')
def warning_feature(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('motor:export_all')
@waflib.TaskGen.before_method('process_source')
def process_export_all_flag(task_gen: waflib.TaskGen.task_gen) -> None:
    task_gen.env.append_unique('CFLAGS', task_gen.env.CFLAGS_exportall)
    task_gen.env.append_unique('CXXFLAGS', task_gen.env.CXXFLAGS_exportall)


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
@waflib.TaskGen.before_method('process_source')
def set_extra_flags(task_gen: waflib.TaskGen.task_gen) -> None:
    for f in getattr(task_gen, 'features', []):
        task_gen.env.append_unique('CLT_CXXFLAGS', task_gen.env['CLT_CXXFLAGS_%s' % f])
        task_gen.env.append_unique('CPPFLAGS', task_gen.env['CPPFLAGS_%s' % f])
        task_gen.env.append_unique('CFLAGS', task_gen.env['CFLAGS_%s' % f])
        task_gen.env.append_unique('CXXFLAGS', task_gen.env['CXXFLAGS_%s' % f])
        task_gen.env.append_unique('LINKFLAGS', task_gen.env['LINKFLAGS_%s' % f])
        task_gen.env.append_unique('LIB', task_gen.env['LIB_%s' % f])
        task_gen.env.append_unique('STLIB', task_gen.env['STLIB_%s' % f])


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
def process_warning_flags(task_gen: waflib.TaskGen.task_gen) -> None:
    warning_flag_name = 'warnnone' if 'motor:warnings:off' in task_gen.features else 'warnall'
    for var in waflib.Tools.ccroot.get_uselib_vars(task_gen):
        task_gen.env.append_value(var, task_gen.env['%s_%s' % (var, warning_flag_name)])


@waflib.TaskGen.feature('cxxshlib', 'cshlib')
def motor_build_dll(task_gen: waflib.TaskGen.task_gen) -> None:
    try:
        getattr(task_gen, 'export_defines').append('motor_dll_%s' % _safe_target_name(task_gen.target))
    except AttributeError:
        setattr(task_gen, 'export_defines', ['motor_dll_%s' % _safe_target_name(task_gen.target)])


@waflib.TaskGen.feature('cxxobjects', 'cobjects')
def motor_build_objects(task_gen: waflib.TaskGen.task_gen) -> None:
    if not task_gen.env.STATIC:
        try:
            getattr(task_gen, 'export_defines').append('motor_dll_%s' % _safe_target_name(task_gen.target))
        except AttributeError:
            setattr(task_gen, 'export_defines', ['motor_dll_%s' % _safe_target_name(task_gen.target)])


def _check_use_taskgens(task_gen: waflib.TaskGen.task_gen) -> None:
    """
    Checks all names in 'use' are valid task generators, or move them to uselib
    """
    for var in 'use', 'private_use':
        use = getattr(task_gen, var, [])
        for name in use[:]:
            try:
                task_gen.bld.get_tgen_by_name(name)
            except waflib.Errors.WafError:
                use.remove(name)
                try:
                    getattr(task_gen, 'uselib').append(name)
                except AttributeError:
                    setattr(task_gen, 'uselib', [name])


def _process_use_flags(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'motor:nortc' not in task_gen.features:
        task_gen.env.append_unique('CFLAGS', task_gen.env.CFLAGS_rtc)
        task_gen.env.append_unique('CFLAGS_debug', task_gen.env.CFLAGS_debug_rtc)
        task_gen.env.append_unique('CFLAGS_profile', task_gen.env.CFLAGS_profile_rtc)
        task_gen.env.append_unique('CFLAGS_final', task_gen.env.CFLAGS_final_rtc)
        task_gen.env.append_unique('CXXFLAGS', task_gen.env.CXXFLAGS_rtc)
        task_gen.env.append_unique('CXXFLAGS_debug', task_gen.env.CXXFLAGS_debug_rtc)
        task_gen.env.append_unique('CXXFLAGS_profile', task_gen.env.CXXFLAGS_profile_rtc)
        task_gen.env.append_unique('CXXFLAGS_final', task_gen.env.CXXFLAGS_final_rtc)
    else:
        task_gen.env.append_unique('CFLAGS', task_gen.env.CFLAGS_nortc)
        task_gen.env.append_unique('CFLAGS_debug', task_gen.env.CFLAGS_debug_nortc)
        task_gen.env.append_unique('CFLAGS_profile', task_gen.env.CFLAGS_profile_nortc)
        task_gen.env.append_unique('CFLAGS_final', task_gen.env.CFLAGS_final_nortc)
        task_gen.env.append_unique('CXXFLAGS', task_gen.env.CXXFLAGS_nortc)
        task_gen.env.append_unique('CXXFLAGS_debug', task_gen.env.CXXFLAGS_debug_nortc)
        task_gen.env.append_unique('CXXFLAGS_profile', task_gen.env.CXXFLAGS_profile_nortc)
        task_gen.env.append_unique('CXXFLAGS_final', task_gen.env.CXXFLAGS_final_nortc)
    dependencies = [task_gen.bld.get_tgen_by_name(i) for i in
                    getattr(task_gen, 'use', []) + getattr(task_gen, 'private_use', [])]
    seen = {task_gen}
    while dependencies:
        dep = dependencies.pop(0)
        if dep not in seen:
            seen.add(dep)
            dep.post()
            dependencies += [task_gen.bld.get_tgen_by_name(i) for i in getattr(dep, 'use', [])]
            for var in waflib.Tools.ccroot.get_uselib_vars(task_gen):
                value = getattr(dep, 'export_%s' % var.lower(), [])
                task_gen.env.append_value(var, waflib.Utils.to_list(value))


def _add_objects_from_tgen(task_gen: waflib.TaskGen.task_gen, depends: waflib.TaskGen.task_gen) -> None:
    try:
        link_task = getattr(task_gen, 'link_task')
    except AttributeError:
        pass
    else:
        for tsk in getattr(depends, 'compiled_tasks', []):
            link_task.inputs.append(tsk.outputs[0])


def _process_use_link(task_gen: waflib.TaskGen.task_gen) -> None:
    link_task = getattr(task_gen, 'link_task', None)
    if link_task:
        dependencies = [
            (task_gen.bld.get_tgen_by_name(i), True) for i in
            getattr(task_gen, 'use', []) + getattr(task_gen, 'private_use', [])
        ]
        all_deps = dependencies[::]
        seen = {task_gen}
        while dependencies:
            dep, link_objects = dependencies.pop(0)
            if dep not in seen:
                seen.add(dep)
                dep.post()
                link_objects = link_objects and not hasattr(dep, 'link_task')
                new_deps = [task_gen.bld.get_tgen_by_name(i) for i in
                            getattr(dep, 'use') + getattr(dep, 'private_use', [])]
                for d in new_deps:
                    try:
                        all_deps.remove((d, link_objects))
                    except ValueError:
                        pass
                    all_deps.append((d, link_objects))
                dependencies += [(i, link_objects) for i in new_deps]
        for d, link_objects in all_deps:
            for var in 'LIB', 'LIBPATH', 'STLIB', 'STLIBPATH', 'LINKFLAGS', 'FRAMEWORK':
                value = getattr(d, 'export_%s' % var.lower(), [])
                task_gen.env.append_value(var, waflib.Utils.to_list(value))
            if 'cxxstlib' in d.features or 'cstlib' in d.features:
                dep_link_task = getattr(d, 'link_task')  # type: waflib.Task.Task
                task_gen.env.append_value('STLIB', [os.path.basename(d.target)])
                link_task.dep_nodes.extend(dep_link_task.outputs)
                tmp_path = dep_link_task.outputs[0].parent.path_from(task_gen.bld.bldnode)
                task_gen.env.append_value('STLIBPATH', [tmp_path])
            elif 'cxxshlib' in d.features or 'cshlib' in d.features:
                dep_link_task = getattr(d, 'link_task')
                task_gen.env.append_value('LIB', [os.path.basename(d.target)])
                link_task.dep_nodes.extend(dep_link_task.outputs)
                tmp_path = dep_link_task.outputs[0].parent.path_from(task_gen.bld.bldnode)
                task_gen.env.append_value('LIBPATH', [tmp_path])
            elif link_objects and ('cxxobjects' in d.features or 'cobjects' in d.features):
                _add_objects_from_tgen(task_gen, d)


# overrides process_use from task_gen
@waflib.TaskGen.taskgen_method
def process_use(task_gen: waflib.TaskGen.task_gen) -> None:
    _check_use_taskgens(task_gen)
    _process_use_link(task_gen)
    _process_use_flags(task_gen)
    uselib = waflib.Utils.to_list(getattr(task_gen, 'uselib', []))
    for x in getattr(task_gen, 'use', []):
        y = task_gen.bld.get_tgen_by_name(x)
        for k in task_gen.to_list(getattr(y, 'uselib', [])):
            if not task_gen.env['STLIB_' + k] and k not in uselib:
                uselib.append(k)
    setattr(task_gen, 'uselib', uselib)


def _make_bld_node(
        task_gen: waflib.TaskGen.task_gen,
        node: waflib.Node.Node,
        category: str,
        path: Optional[Union[waflib.Node.Node, str]],
        name: str
) -> waflib.Node.Node:
    node = node.make_node(category)
    if not path:
        node = node.make_node(name)
    elif isinstance(path, waflib.Node.Node):
        if path.is_child_of(task_gen.bld.bldnode):
            out_dir = path.path_from(task_gen.bld.bldnode)
            # skip variant
            # out_dir = out_dir[out_dir.find(os.path.sep)+1:]
            # skip optim
            # out_dir = out_dir[out_dir.find(os.path.sep)+1:]
            # skip target
            out_dir = out_dir[out_dir.find(os.path.sep) + 1:]
            # skip category
            out_dir = out_dir[out_dir.find(os.path.sep) + 1:]
            node = node.make_node(out_dir)
            node = node.make_node(name)
        elif path.is_child_of(task_gen.bld.bldnode.parent.parent):
            out_dir = path.path_from(task_gen.bld.bldnode.parent.parent)
            # skip variant
            # out_dir = out_dir[out_dir.find(os.path.sep)+1:]
            # skip optim
            # out_dir = out_dir[out_dir.find(os.path.sep)+1:]
            # skip target
            out_dir = out_dir[out_dir.find(os.path.sep) + 1:]
            # skip category
            out_dir = out_dir[out_dir.find(os.path.sep) + 1:]
            node = node.make_node(out_dir)
            node = node.make_node(name)
        else:
            out_dir = ''
            for _, source_node in getattr(task_gen, 'source_nodes', []):
                if path.is_child_of(source_node):
                    for child in source_node.children.values():
                        if path.is_child_of(child):
                            out_dir = path.path_from(child)
                            break
                    break
            else:
                out_dir = path.path_from(task_gen.path)
            while out_dir[0] == '.' and len(out_dir) > 2:
                out_dir = out_dir[out_dir.find(os.path.sep) + 1:]
            node = node.make_node(out_dir)
            node = node.make_node(name)
    else:
        node = node.make_node(path)
        node = node.make_node(name)
    if not task_gen.env.PROJECTS:
        node.parent.mkdir()
    return node


def make_bld_node(
        task_gen: waflib.TaskGen.task_gen,
        category: str,
        path: Optional[Union[waflib.Node.Node, str]],
        name: str
) -> waflib.Node.Node:
    """
        constructs a path from the target build node:
            build_node/variant/optim/target/category/path/name
    """
    return _make_bld_node(task_gen, task_gen.bld.bldnode.make_node(task_gen.target), category, path, name)


def apply_source_filter(
        task_gen: waflib.TaskGen.task_gen,
        env: waflib.ConfigSet.ConfigSet,
        file: waflib.Node.Node
) -> Tuple[bool, bool]:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    basename, _ = os.path.splitext(file.name)
    add_platform = True
    add_arch = True
    add_compiler = True
    had_filter = False

    platform = file.name.find('-p=')
    if platform != -1:
        had_filter = True
        add_platform = False
        platforms = basename[platform + 3:].split('+')
        for p in platforms:
            add_platform = add_platform or p in env.VALID_PLATFORMS
    arch = file.name.find('-a=')
    if arch != -1:
        had_filter = True
        add_arch = False
        architectures = basename[arch + 3:].split('+')
        for a in architectures:
            add_arch = add_arch or a in env.VALID_ARCHITECTURES
    compiler = file.name.find('-c=')
    if compiler != -1:
        had_filter = True
        add_compiler = False
        compilers = basename[compiler + 3:].split('+')
        for c in compilers:
            add_compiler = add_compiler or c == env.COMPILER_NAME
    node = file.parent
    while (add_platform and add_arch and add_compiler
           and node and node != task_gen.path and node != task_gen.bld.srcnode):
        if node.name.startswith('platform='):
            had_filter = True
            add_platform = False
            platforms = node.name[9:].split('+')
            for p in platforms:
                add_platform = add_platform or p in env.VALID_PLATFORMS
        elif node.name.startswith('arch='):
            had_filter = True
            add_arch = False
            architectures = node.name[5:].split('+')
            for a in architectures:
                add_arch = add_arch or a in env.VALID_ARCHITECTURES
        elif node.name.startswith('compiler='):
            had_filter = True
            add_compiler = False
            compilers = node.name[9:].split('+')
            for c in compilers:
                add_compiler = add_compiler or c == env.COMPILER_NAME
        elif node.parent.name == 'extra' and node.parent.parent == task_gen.bld.motornode:
            had_filter = True
            add_platform = add_platform and node.name in env.VALID_PLATFORMS
        node = node.parent
    return add_platform and add_arch and add_compiler, had_filter


@waflib.TaskGen.feature('*')
@waflib.TaskGen.before_method('process_source')
def filter_sources(task_gen: waflib.TaskGen.task_gen) -> None:
    preprocess_step = getattr(task_gen, 'preprocess', None)
    if preprocess_step is not None:
        preprocess_step.post()
        task_gen.source += preprocess_step.out_sources
    has_objc = False
    task_gen.source = waflib.TaskGen.to_nodes(task_gen, getattr(task_gen, 'source', []))
    if task_gen.env.PROJECTS:
        return
    sources = []
    for file in task_gen.source:
        if apply_source_filter(task_gen, task_gen.env, file)[0]:
            sources.append(file)
            _, ext = os.path.splitext(file.name)
            if ext in ['.m', '.mm']:
                has_objc = True
    setattr(task_gen, 'objc', has_objc)
    task_gen.source = sources


def create_compiled_task(
        task_gen: waflib.TaskGen.task_gen,
        compiler_name: str,
        source_node: waflib.Node.Node
) -> waflib.Task.Task:
    out = make_bld_node(task_gen, 'obj', source_node.parent, source_node.name[:source_node.name.rfind('.')] + '.o')
    task = task_gen.create_task(compiler_name, [source_node], [out])
    extra_env = task_gen.env['%s_env' % compiler_name]
    if extra_env:
        if not task.env.env:
            task.env.env = dict(os.environ)
        for k, v in extra_env:
            task.env.env[k] = v
    try:
        getattr(task_gen, 'compiled_tasks').append(task)
    except AttributeError:
        setattr(task_gen, 'compiled_tasks', [task])
    return task


@waflib.TaskGen.extension('.def')
def def_file(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    try:
        getattr(task_gen, 'def_files').append(node)
    except AttributeError:
        setattr(task_gen, 'def_files', [node])


@waflib.TaskGen.extension('.rc')
def rc_file(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    """
    Bind the .rc extension to a winrc task
    """
    if not task_gen.env.WINRC:
        return
    obj_ext = '.o'
    if task_gen.env['WINRC_TGT_F'] == '/fo':
        obj_ext = '.res'
    out = make_bld_node(task_gen, 'obj', node.parent, node.name[:node.name.rfind('.')] + obj_ext)
    rctask = task_gen.create_task('winrc', [node], [out])
    rctask.env.PATH = []
    try:
        getattr(task_gen, 'compiled_tasks').append(rctask)
    except AttributeError:
        setattr(task_gen, 'compiled_tasks', [rctask])


@waflib.TaskGen.feature('c', 'cxx')
@waflib.TaskGen.after_method('process_source')
def apply_link(task_gen: waflib.TaskGen.task_gen) -> None:
    for x in task_gen.features:
        if x == 'cprogram' and 'cxx' in task_gen.features:  # limited compat
            x = 'cxxprogram'
        elif x == 'cshlib' and 'cxx' in task_gen.features:
            x = 'cxxshlib'
        if x in waflib.Task.classes:
            if issubclass(waflib.Task.classes[x], waflib.Tools.ccroot.link_task):
                link = x
                break
    else:
        return

    objs = [t.outputs[0] for t in getattr(task_gen, 'compiled_tasks', [])]
    link_task = task_gen.create_task(link, objs)
    setattr(task_gen, 'link_task', link_task)
    pattern = task_gen.env['%s_PATTERN' % link]
    if not pattern:
        pattern = '%s'
    path, name = os.path.split(task_gen.target)
    out_node = _make_bld_node(task_gen, task_gen.bld.bldnode, 'bin', None, os.path.join(path, pattern % name))
    link_task.set_outputs(out_node)


@waflib.TaskGen.feature('cprogram', 'cxxprogram', 'cshlib', 'cxxshlib')
@waflib.TaskGen.after_method('apply_link')
@waflib.TaskGen.before_method('install_step')
def set_postlink_task(task_gen: waflib.TaskGen.task_gen) -> None:
    setattr(task_gen, 'postlink_task', getattr(task_gen, 'link_task'))


@waflib.TaskGen.feature('cprogram', 'cxxprogram', 'cshlib', 'cxxshlib')
@waflib.TaskGen.after_method('set_postlink_task')
def install_step(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('motor:c', 'motor:cxx')
def set_macosx_deployment_target(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('c', 'cxx', 'd', 'asm', 'fc', 'includes')
@waflib.TaskGen.after_method('propagate_uselib_vars', 'process_source')
def apply_incpaths(task_gen: waflib.TaskGen.task_gen) -> None:
    """
    Task generator method that processes the attribute *includes*::

        tg = bld(features='includes', includes='.')

    The folders only need to be relative to the current directory, the equivalent build directory is
    added automatically (for headers created in the build directory). This enable using a build directory
    or not (``top == out``).

    This method will add a list of nodes read by :py:func:`waflib.Tools.ccroot.to_incnodes` in ``tg.env.INCPATHS``,
    and the list of include paths in ``tg.env.INCLUDES``.
    """
    lst = waflib.Tools.ccroot.to_incnodes(task_gen,
                                          task_gen.to_list(getattr(task_gen, 'includes', [])) + task_gen.env.INCLUDES)
    setattr(task_gen, 'includes_nodes', lst)
    task_gen.env.INCPATHS = [x.abspath() for x in lst]
    lst = waflib.Tools.ccroot.to_incnodes(task_gen, task_gen.env.SYSTEM_INCLUDES)
    for system_include in [x.abspath() for x in lst]:
        task_gen.env.append_value('CFLAGS', [task_gen.env.IDIRAFTER, system_include])
        task_gen.env.append_value('CXXFLAGS', [task_gen.env.IDIRAFTER, system_include])
