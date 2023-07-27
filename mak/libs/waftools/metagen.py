#!/usr/bin/env python
# encoding: utf-8

from waflib import Task, Errors, Options
from waflib.TaskGen import extension, feature, before_method, after_method
import sys
import pickle


class metagen(Task.Task):
    color = 'BLUE'
    ext_in = ['.h', '.hh', '.hxx']
    ext_out = ['.cc']

    def run(self):
        werror = []
        if Options.options.werror:
            werror.append('-Werror')
        return self.exec_command(
            [
                sys.executable,
                self.metagen.abspath(),
                '-x',
                'c++',
                '--std',
                'c++14',
                '-D',
                self.macros.abspath(),
                '--module',
                self.generator.env.PLUGIN,
                '--root',
                self.generator.root_namespace,
                '--tmp',
                self.generator.bld.bldnode.parent.parent.abspath(),
            ] + werror + [
                self.inputs[0].path_from(self.generator.bld.bldnode),
                self.inputs[0].path_from(self.generator.bld.srcnode),
                self.outputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[1].path_from(self.generator.bld.bldnode),
                self.outputs[2].path_from(self.generator.bld.bldnode),
                self.outputs[3].path_from(self.generator.bld.bldnode),
            ]
        )

    def scan(self):
        return ([], [])


namespace_register = 'MOTOR_REGISTER_NAMESPACE_%d_NAMED(%s, %s)\n'
namespace_alias = 'MOTOR_REGISTER_ROOT_NAMESPACE(%s, %s, %s)\n'


class docgen(Task.Task):

    def process_node(self, node):
        return []

    def run(self):
        for input in self.inputs:
            self.outputs += self.process_node(input)
        return 0


class ns_export(Task.Task):

    def run(self):
        seen = set([])
        with open(self.outputs[0].abspath(), 'w') as export_file:
            pch = getattr(self, 'pch', '')
            if pch:
                export_file.write('#include <%s>\n' % pch)
            export_file.write('#include <motor/meta/namespace.hh>\n')
            for input in self.inputs:
                with open(input.abspath(), 'rb') as in_file:
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


class cls_export(Task.Task):

    def run(self):
        seen = set([])
        with open(self.outputs[0].abspath(), 'w') as export_file:
            pch = getattr(self, 'pch', '')
            if pch:
                export_file.write('#include <%s>\n' % pch)
            export_file.write('#include <motor/meta/typeinfo.hh>\n')
            for input in self.inputs:
                with open(input.abspath(), 'rb') as in_file:
                    plugin, root_namespace, include = pickle.load(in_file)
                    export_file.write('#include <%s>\n' % include)
                    root_namespace = root_namespace.split('::')
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


@extension('.h', '.hh', '.hxx')
def datagen(self, node):
    outs = []
    out_node = self.make_bld_node('src', node.parent, '%s.cc' % node.name[:node.name.rfind('.')])
    out_node.parent.mkdir()
    outs.append(out_node)
    outs.append(out_node.change_ext('.doc'))
    outs.append(out_node.change_ext('.class_exports'))
    outs.append(out_node.change_ext('.namespace_exports'))

    tsk = self.create_task(
        'metagen',
        node,
        outs,
        metagen=self.bld.motornode.find_node('mak/tools/bin/metagen.py'),
        macros=self.bld.motornode.find_node('mak/tools/macros_def.json'),
    )
    tsk.dep_nodes = self.bld.pyxx_nodes + [self.bld.motornode.find_node('mak/tools/bin/metagen.py')]

    self.out_sources.append(out_node)
    self.source.append(outs[1])
    self.source.append(outs[2])
    self.source.append(outs[3])


@feature('motor:module')
def dummy_feature_module(self):
    pass


@feature('motor:shared_lib', 'motor:launcher', 'motor:unit_test', 'motor:python_module')
@before_method('process_source')
@before_method('filter_sources')
@after_method('static_dependencies')
def namespace_exports_gen(self):
    # gather all exports of dependencies
    preprocess = getattr(self, 'preprocess')
    seen = set([])
    use = getattr(self, 'use', [])[:]
    while (use):
        x = use.pop()
        if x in seen:
            continue
        seen.add(x)
        try:
            y = self.bld.get_tgen_by_name(x)
        except Errors.WafError:
            pass
        else:
            y.post()
            y_p = getattr(y, 'preprocess', None)
            if y_p is not None:
                if 'motor:module' not in y_p.features:
                    use += getattr(y, 'use', [])
                    for s in y_p.source:
                        if s.name.endswith('.namespace_exports'):
                            preprocess.add_namespace_export_file(s)


@extension('.namespace_exports')
def add_namespace_export_file(self, node):
    if 'motor:module' not in self.features:
        return
    try:
        self.namespace_exports_task.set_inputs([node])
    except AttributeError:
        out_node = self.make_bld_node('src', None, 'meta_namespace_export.cc')
        self.out_sources.append(out_node)
        self.nomaster.add(out_node)
        self.namespace_exports_task = self.create_task('ns_export', [node], [out_node])


@extension('.class_exports')
def add_class_export_file(self, node):
    try:
        self.class_exports_task.set_inputs([node])
    except AttributeError:
        out_node = self.make_bld_node('src', None, 'meta_class_export.cc')
        self.out_sources.append(out_node)
        self.nomaster.add(out_node)
        self.class_exports_task = self.create_task('cls_export', [node], [out_node])


@extension('.doc')
def add_doc(self, node):
    if self.source_nodes[0][1].is_child_of(self.bld.motornode):
        out_node = self.bld.motornode
    else:
        out_node = self.bld.srcnode
    doc_task = self.create_task('docgen', [], [])
    doc_task.out_dir = out_node.make_node('docs/api')
    doc_task.out_dir.mkdir()
    doc_task.set_inputs([node])
