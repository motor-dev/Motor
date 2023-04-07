#!/usr/bin/env python
# encoding: utf-8

from waflib import Task
from waflib.TaskGen import extension, feature, before_method, after_method
import sys
import pickle


class metagen(Task.Task):
    color = 'BLUE'
    ext_in = ['.h', '.hh', '.hxx']
    ext_out = ['.cc']

    def run(self):
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
                self.generator.bld.bldnode.parent.abspath(),
                self.inputs[0].path_from(self.generator.bld.bldnode),
                self.inputs[0].path_from(self.generator.bld.srcnode),
                self.outputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[1].path_from(self.generator.bld.bldnode),
                self.outputs[2].path_from(self.generator.bld.bldnode),
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


class nsdef(Task.Task):

    def run(self):
        seen = set([])
        with open(self.outputs[0].abspath(), 'w') as namespace_file:
            pch = getattr(self, 'pch', '')
            if pch:
                namespace_file.write('#include <%s>\n' % pch)
            namespace_file.write('#include <motor/meta/engine/namespace.hh>\n')
            for input in self.inputs:
                with open(input.abspath(), 'rb') as in_file:
                    plugin, root_namespace = pickle.load(in_file)
                    root_namespace = root_namespace.split('::')
                    while True:
                        try:
                            namespace = pickle.load(in_file)
                            if (plugin, '.'.join(namespace)) not in seen:
                                seen.add((plugin, '.'.join(namespace)))
                                if namespace == root_namespace:
                                    line = namespace_alias % (
                                        plugin, '_' + '_'.join(root_namespace[:-1]) if len(root_namespace) > 1 else '',
                                        root_namespace[-1]
                                    )
                                else:
                                    line = namespace_register % (len(namespace), plugin, ', '.join(namespace))
                                namespace_file.write(line)
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
    outs.append(out_node.change_ext('.namespaces'))

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


@feature('motor:module')
@before_method('process_source')
@after_method('static_dependencies')
def nsgen(self):
    # gather all namespaces of dependencies
    seen = set([])
    use = getattr(self, 'use', [])[:]
    while (use):
        x = use.pop()
        if x in seen:
            continue
        seen.add(x)
        try:
            y = self.bld.get_tgen_by_name(x)
        except:
            pass
        else:
            y.post()
            if 'motor:module' not in y.features:
                use += getattr(y, 'use', [])
                for s in y.source:
                    if s.name.endswith('.namespaces'):
                        self.add_namespace_file(s)


@extension('.namespaces')
def add_namespace_file(self, node):
    if 'motor:module' not in self.features:
        return
    try:
        self.namespace_task.set_inputs([node])
    except AttributeError:
        out_node = self.make_bld_node('src', None, 'namespace_definition.cc')
        self.out_sources.append(out_node)
        self.namespace_task = self.create_task('nsdef', [node], [out_node])


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
