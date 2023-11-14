import os
import shlex
import waflib.TaskGen
import waflib.Node
import waflib.Logs
import waflib.Task
import waflib.Utils
import waflib.Errors
import waflib.Options
from ...options import BuildContext

from typing import List, Callable, Tuple

from .clang import setup_compiler_clang
from .gcc import setup_compiler_gcc
from .icc import setup_compiler_icc
from .msvc import setup_compiler_msvc
from .suncc import setup_compiler_suncc


@waflib.TaskGen.feature('c', 'cxx')
@waflib.TaskGen.after_method('process_source')
@waflib.TaskGen.after_method('generate_export_file')
def add_dependency_file(task_gen: waflib.TaskGen.task_gen) -> None:
    if task_gen.env.ENABLE_COMPILER_DEPS:
        for task in getattr(task_gen, 'compiled_tasks', []):
            if task and task.__class__.__name__ in ('cxx', 'c'):
                task.outputs.append(task.outputs[0].change_ext('.d'))


def _paths_to_nodes(src_node: waflib.Node.Node, bld_node: waflib.Node.Node, paths: List[str]) -> List[waflib.Node.Node]:
    bld_path = os.path.normcase(os.path.normpath(bld_node.abspath()))
    src_path = os.path.normcase(os.path.normpath(src_node.abspath()))
    result = []
    for path in paths:
        if os.path.isabs(path):
            path = os.path.normcase(os.path.normpath(path))

            if path[:len(bld_path)] == bld_path:
                node = bld_node.find_node(os.path.relpath(path, bld_path))
            elif path[:len(src_path)] == src_path:
                node = src_node.find_node(os.path.relpath(path, src_path))
            else:
                continue
            assert node
            result.append(node)
        else:
            node = bld_node.find_node(path)
            if not node:
                print(path)
            assert node, path
            result.append(node)
    return result


def _compiler_deps_scan(
        original_scan: Callable[[waflib.Task.Task], Tuple[List[waflib.Node.Node], List[str]]]
) -> Callable[[waflib.Task.Task], Tuple[List[waflib.Node.Node], List[str]]]:
    def scan(self: waflib.Task.Task) -> Tuple[List[waflib.Node.Node], List[str]]:
        if not self.env.ENABLE_COMPILER_DEPS:
            return original_scan(self)
        nodes = self.generator.bld.node_deps.get(self.uid(), [])
        return nodes, []

    return scan


def _compiler_deps_post_run(
        original_post_run: Callable[[waflib.Task.Task], None]
) -> Callable[[waflib.Task.Task], None]:
    def post_run(self: waflib.Task.Task) -> None:
        if self.env.ENABLE_COMPILER_DEPS:
            bld = self.generator.bld
            deps_node = self.outputs[0].change_ext('.d')
            try:
                txt = deps_node.read()
            except EnvironmentError:
                waflib.Logs.error('Could not find a .d dependency file, are cflags/cxxflags properly installed?')
                raise
            lines = txt.replace('\\\n', ' ').replace('\\\r\n', ' ').replace('\\', '\\\\').split('\n')
            dependencies = []
            for line in lines:
                if not line:
                    continue
                deps = shlex.split(line)
                if deps[0][-1] == ':':
                    dependencies += deps[1:]
                elif deps[1] == ':':
                    dependencies += deps[2:]
                else:
                    assert False

            node_dependencies = _paths_to_nodes(bld.srcnode, bld.bldnode, dependencies)
            node_dependencies = [d for d in node_dependencies if id(d) != id(self.inputs[0])]
            bld.node_deps[self.uid()] = node_dependencies
            bld.raw_deps[self.uid()] = []

            try:
                del self.cache_sig
            except AttributeError:
                pass
            waflib.Task.Task.post_run(self)
        else:
            return original_post_run(self)

    return post_run


def _compiler_deps_sig_implicit_deps(
        original_sig_implicit_deps: Callable[[waflib.Task.Task], bytes]
) -> Callable[[waflib.Task.Task], bytes]:
    def sig_implicit_deps(self: waflib.Task.Task) -> bytes:
        if not self.env.ENABLE_COMPILER_DEPS:
            return original_sig_implicit_deps(self)
        try:
            return waflib.Task.Task.sig_implicit_deps(self)
        except OSError:
            return waflib.Utils.SIG_NIL

    return sig_implicit_deps


def setup_build_compiler(build_context: BuildContext) -> None:
    for cls_name in 'c', 'cxx':
        cls = waflib.Task.classes.get(cls_name, None)
        if cls is not None:
            derived = type(cls_name, (cls,), {})
            setattr(derived, 'scan', _compiler_deps_scan(getattr(derived, 'scan')))
            setattr(derived, 'post_run', _compiler_deps_post_run(getattr(derived, 'post_run')))
            setattr(derived, 'sig_implicit_deps',
                    _compiler_deps_sig_implicit_deps(getattr(derived, 'sig_implicit_deps')))

    setup_compiler_clang(build_context)
    setup_compiler_gcc(build_context)
    setup_compiler_icc(build_context)
    setup_compiler_msvc(build_context)
    setup_compiler_suncc(build_context)

    if waflib.Options.options.werror:
        build_context.env.append_unique('CFLAGS', build_context.env.CFLAGS_werror)
        build_context.env.append_unique('CXXFLAGS', build_context.env.CXXFLAGS_werror)
