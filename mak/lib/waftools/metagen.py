import sys
import pickle
import build_framework
import waflib.Configure
import waflib.Errors
import waflib.Node
import waflib.Options
import waflib.Task
import waflib.TaskGen
from typing import List, Tuple


class metagen(waflib.Task.Task):
    color = 'BLUE'
    ext_in = ['.h', '.hh', '.hxx']
    ext_out = ['.cc']

    def run(self) -> int:
        metagen_node = getattr(self, 'metagen')  # type: waflib.Node.Node
        macros_node = getattr(self, 'macros')  # type: waflib.Node.Node
        extra_options = []
        if waflib.Options.options.werror:
            extra_options.append('-Werror')
        if sys.stdout.isatty():
            extra_options.append('--diagnostics-color')
        return self.exec_command(
            [
                sys.executable,
                metagen_node.abspath(),
                '-x',
                'c++',
                '--std',
                'c++14',
                '-D',
                macros_node.abspath(),
                '--module',
                self.generator.env.PLUGIN,
                '--root',
                getattr(self.generator, 'root_namespace'),
                '--tmp',
                self.generator.bld.bldnode.abspath(),
            ] + extra_options + [
                self.inputs[0].path_from(self.generator.bld.bldnode),
                self.inputs[0].path_from(self.generator.bld.srcnode),
                self.outputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[1].path_from(self.generator.bld.bldnode),
                self.outputs[2].path_from(self.generator.bld.bldnode),
                self.outputs[3].path_from(self.generator.bld.bldnode),
            ]
        )

    # noinspection PyMethodMayBeStatic
    def scan(self) -> Tuple[List[waflib.Node.Node], List[str]]:  # type: ignore
        return [], []


namespace_register = 'MOTOR_REGISTER_NAMESPACE_%d_NAMED(%s, %s)\n'
namespace_alias = 'MOTOR_REGISTER_ROOT_NAMESPACE(%s, %s, %s)\n'


class docgen(waflib.Task.Task):

    # noinspection PyMethodMayBeStatic
    def process_node(self, _: waflib.Node.Node) -> List[waflib.Node.Node]:
        return []

    def run(self) -> int:
        for input_node in self.inputs:
            self.outputs += self.process_node(input_node)
        return 0


class ns_export(waflib.Task.Task):

    def run(self) -> int:
        seen = set([])
        with open(self.outputs[0].abspath(), 'w') as export_file:
            pch = getattr(self, 'pch', '')
            if pch:
                export_file.write('#include <%s>\n' % pch)
            export_file.write('#include <motor/meta/namespace.hh>\n')
            for input_node in self.inputs:
                with open(input_node.abspath(), 'rb') as in_file:
                    plugin, root_namespace, include = pickle.load(in_file)
                    root_namespace = root_namespace.split('::')
                    while True:
                        try:
                            full_name = pickle.load(in_file)
                            if (plugin, '.'.join(full_name)) not in seen:
                                seen.add((plugin, '.'.join(full_name)))
                                if full_name == root_namespace:
                                    line = namespace_alias % (
                                        plugin,
                                        '_' + '_'.join(root_namespace[:-1]) if len(root_namespace) > 1 else '',
                                        root_namespace[-1]
                                    )
                                else:
                                    line = namespace_register % (len(full_name), plugin, ', '.join(full_name))
                                export_file.write(line)
                        except EOFError:
                            break
        return 0


class cls_export(waflib.Task.Task):

    def run(self) -> int:
        with open(self.outputs[0].abspath(), 'w') as export_file:
            pch = getattr(self, 'pch', '')
            if pch:
                export_file.write('#include <%s>\n' % pch)
            export_file.write('#include <motor/meta/typeinfo.hh>\n')
            for input_node in self.inputs:
                with open(input_node.abspath(), 'rb') as in_file:
                    plugin, root_namespace, include = pickle.load(in_file)
                    export_file.write('#include <%s>\n' % include)
                    while True:
                        try:
                            namespace, class_name = pickle.load(in_file)
                            namespace_name = namespace + ['%s_Meta' % s for s in class_name]
                            class_name = '::'.join(namespace + class_name)
                            export_file.write(
                                'namespace %s {\n'
                                'extern raw<Motor::Meta::Class> klass();\n'
                                'extern Motor::istring name();\n'
                                '%s\n'
                                'template<>\n'
                                'MOTOR_EXPORT raw< const ::Motor::Meta::Class > Motor::Meta::ClassID<%s>::klass()\n'
                                '{\n'
                                '    return %s::klass();\n'
                                '};\n'
                                'template<>\n'
                                'MOTOR_EXPORT Motor::istring Motor::Meta::ClassID<::%s>::name()\n'
                                '{\n'
                                '    static const istring s_name = %s::name();\n'
                                '    return s_name;\n'
                                '};\n' % (
                                    ' { namespace '.join(namespace_name), '}' * len(namespace_name),
                                    class_name, '::'.join(namespace_name), class_name, '::'.join(namespace_name))
                            )
                        except EOFError:
                            break
        return 0


@waflib.TaskGen.extension('.h', '.hh', '.hxx')
def datagen(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    outs = []
    out_node = build_framework.make_bld_node(task_gen, 'src', node.parent, '%s.cc' % node.name[:node.name.rfind('.')])
    out_node.parent.mkdir()
    outs.append(out_node)
    outs.append(out_node.change_ext('.doc'))
    outs.append(out_node.change_ext('.class_exports'))
    outs.append(out_node.change_ext('.namespace_exports'))

    tsk = task_gen.create_task(
        'metagen',
        [node],
        outs,
        metagen=task_gen.bld.motornode.make_node('mak/bin/metagen.py'),
        macros=task_gen.bld.motornode.make_node('mak/tools/macros_def.json'),
    )
    tsk.dep_nodes = task_gen.bld.pyxx_nodes + [task_gen.bld.motornode.make_node('mak/bin/metagen.py')]

    getattr(task_gen, 'out_sources').append(out_node)
    task_gen.source.append(outs[1])
    task_gen.source.append(outs[2])
    task_gen.source.append(outs[3])


@waflib.TaskGen.feature('motor:module')
def dummy_feature_module(_: waflib.TaskGen.task_gen) -> None:
    pass


@waflib.TaskGen.feature('motor:module')
@waflib.TaskGen.before_method('process_source')
@waflib.TaskGen.before_method('filter_sources')
@waflib.TaskGen.after_method('static_preprocess_dependencies')
def namespace_exports_gen(task_gen: waflib.TaskGen.task_gen) -> None:
    # gather all exports of dependencies
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
            y.post()
            if 'motor:module' not in y.features:
                use += getattr(y, 'use', [])
                for s in y.source:
                    if s.name.endswith('.namespace_exports'):
                        add_namespace_export_file(task_gen, s)


@waflib.TaskGen.extension('.namespace_exports')
def add_namespace_export_file(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    if 'motor:module' not in task_gen.features:
        return
    try:
        getattr(task_gen, 'namespace_exports_task').set_inputs([node])
    except AttributeError:
        out_node = build_framework.make_bld_node(task_gen, 'src', None, 'meta_namespace_export.cc')
        getattr(task_gen, 'out_sources').append(out_node)
        getattr(task_gen, 'nomaster').add(out_node)
        setattr(task_gen, 'namespace_exports_task', task_gen.create_task('ns_export', [node], [out_node]))


@waflib.TaskGen.extension('.class_exports')
def add_class_export_file(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    try:
        getattr(task_gen, 'class_exports_task').set_inputs([node])
    except AttributeError:
        out_node = build_framework.make_bld_node(task_gen, 'src', None, 'meta_class_export.cc')
        getattr(task_gen, 'out_sources').append(out_node)
        getattr(task_gen, 'nomaster').add(out_node)
        setattr(task_gen, 'class_exports_task', task_gen.create_task('cls_export', [node], [out_node]))


@waflib.TaskGen.extension('.doc')
def add_doc(task_gen: waflib.TaskGen.task_gen, node: waflib.Node.Node) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    if getattr(task_gen, 'source_nodes')[0][1].is_child_of(task_gen.bld.motornode):
        out_node = task_gen.bld.motornode
    else:
        out_node = task_gen.bld.srcnode
    doc_task = task_gen.create_task('docgen', [], [])
    # doc_task.out_dir = out_node.make_node('docs/api')
    # doc_task.out_dir.mkdir()
    doc_task.set_inputs([node])
