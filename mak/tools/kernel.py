#!/usr/bin/env python
# encoding: utf-8

from waflib import Task, Errors
from waflib.TaskGen import task_gen, extension, feature, before_method
import os
import sys
import pickle


class kernel(Task.Task):
    color = 'CYAN'

    def run(self):
        return self.exec_command(
            [
                sys.executable,
                self.kernel.abspath(),
                '-x',
                'c++',
                '--std',
                'c++14',
                '-D',
                self.macros.abspath(),
                '--name',
                self.kernel_name,
                '--tmp',
                self.generator.bld.bldnode.parent.parent.abspath(),
                '--module',
                self.generator.parent,
                self.inputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[1].path_from(self.generator.bld.bldnode),
                self.outputs[2].path_from(self.generator.bld.bldnode),
                self.outputs[2].path_from(self.generator.generated_include_node),
            ]
        )


@feature('motor:preprocess')
@before_method('process_source')
def generate_kernel(self):
    kernel_list = getattr(self, 'kernels', [])
    if kernel_list:
        mak_node = self.bld.motornode.make_node('mak')
        dep_nodes = [mak_node.find_node('tools/bin/kernel.py')]
        kernel_node = mak_node.find_node('tools/bin/kernel.py')
        macros_node = mak_node.find_node('tools/macros_def.json')

        for kernel, source in kernel_list:
            out = self.make_bld_node('src/kernels', None, '%s.kernel' % (os.path.join(*kernel)))
            cc = out.change_ext('-kerneltask.cc')
            hh = self.make_bld_node('include/kernels', None, '%s-kerneltask.meta.hh' % (os.path.join(*kernel)))
            out.parent.mkdir()
            hh.parent.mkdir()

            task = self.create_task(
                'kernel',
                [source],
                [out, cc, hh],
                kernel=kernel_node,
                macros=macros_node,
                cpu=os.path.splitext(source.name)[1] in ('.cc', '.cpp'),
                kernel_name='.'.join(kernel),
            )
            task.dep_nodes = self.bld.pyxx_nodes + dep_nodes

            self.source.append(hh)
            self.out_sources.append(cc)


@feature('motor:cxx')
@before_method('process_source')
def process_kernels(task_gen):
    preprocess = getattr(task_gen, 'preprocess', None)
    kernel_list = getattr(preprocess, 'kernels', [])
    for kernel_name, source in kernel_list:
        kernel_node = preprocess.make_bld_node('src/kernels', None, '%s.kernel' % (os.path.join(*kernel_name)))
        for kernel_processor in task_gen.__class__.kernel_processors:
            kernel_processor(task_gen, kernel_name, source, kernel_node, source.name.endswith('.cl') and 'gpu' or 'cpu')


def build(build_context):
    task_gen.kernel_processors = []