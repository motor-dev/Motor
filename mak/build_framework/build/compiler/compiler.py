import os
import shlex
from waflib import Task, TaskGen, Options, Utils, Logs, Errors


@TaskGen.feature('c', 'cxx')
@TaskGen.after_method('process_source')
def add_dependency_file(task_gen):
    if task_gen.env.ENABLE_COMPILER_DEPS:
        for task in getattr(task_gen, 'compiled_tasks', []):
            if task:
                task.outputs.append(task.outputs[0].change_ext('.d'))


def paths_to_nodes(src_node, bld_node, paths):
    bld_path = os.path.normcase(os.path.normpath(bld_node.abspath()))
    src_path = os.path.normcase(os.path.normpath(src_node.abspath()))
    result = []
    for path in paths:
        if os.path.isabs(path):
            path = os.path.normcase(os.path.normpath(path))
            if path[:len(bld_path)] == bld_path:
                result.append(bld_node.find_node(os.path.relpath(path, bld_path)))
            elif path[:len(src_path)] == src_path:
                result.append(src_node.find_node(os.path.relpath(path, src_path)))
        else:
            result.append(bld_node.find_node(path))
    return result


def compiler_deps_scan(original_scan):

    def scan(self):
        if not self.env.ENABLE_COMPILER_DEPS:
            return original_scan(self)
        nodes = self.generator.bld.node_deps.get(self.uid(), [])
        names = []
        return (nodes, names)

    return scan


def compiler_deps_post_run(original_post_run):

    def post_run(self):
        if self.env.ENABLE_COMPILER_DEPS:
            bld = self.generator.bld
            deps_node = self.outputs[0].change_ext('.d')
            try:
                txt = deps_node.read()
            except EnvironmentError:
                Logs.error('Could not find a .d dependency file, are cflags/cxxflags overwritten?')
                raise
            lines = txt.replace('\\\n', ' ').replace('\\\r\n', ' ').split('\n')
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

            dependencies = paths_to_nodes(bld.srcnode, bld.bldnode, dependencies)
            dependencies = [d for d in dependencies if id(d) != id(self.inputs[0])]
            bld.node_deps[self.uid()] = dependencies
            bld.raw_deps[self.uid()] = []

            try:
                del self.cache_sig
            except AttributeError:
                pass
            Task.Task.post_run(self)
        else:
            return original_post_run(self)

    return post_run


def compiler_deps_sig_implicit_deps(original_sig_implicit_deps):

    def sig_implicit_deps(self):
        if not self.env.ENABLE_COMPILER_DEPS:
            return original_sig_implicit_deps(self)
        try:
            return Task.Task.sig_implicit_deps(self)
        except Errors.WafError:
            return Utils.SIG_NIL

    return sig_implicit_deps


def build(build_context):
    for cls_name in 'c', 'cxx':
        cls = Task.classes.get(cls_name, None)
        derived = type(cls_name, (cls, ), {})
        derived.scan = compiler_deps_scan(derived.scan)
        derived.post_run = compiler_deps_post_run(derived.post_run)
        derived.sig_implicit_deps = compiler_deps_sig_implicit_deps(derived.sig_implicit_deps)

    compilers = Options.options.compilers
    compilers = compilers.split(',') if compilers else []
    for compiler in os.listdir(build_context.path.abspath()):
        if not compilers or os.path.splitext(compiler)[0] in compilers:
            build_context.recurse(compiler)
