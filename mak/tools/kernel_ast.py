#!/usr/bin/env python
# encoding: utf-8

from waflib import Task
from waflib.TaskGen import feature, before_method
import os
import sys


class kernel_ast(Task.Task):
    color = 'CYAN'

    def run(self):
        return self.exec_command(
            [
                sys.executable,
                self.kernel.abspath(),
                '-d',
                self.macros.abspath(),
                '--tmp',
                self.generator.bld.bldnode.parent.parent.abspath(),
                '--module',
                self.env.PLUGIN,
                self.kernel_name,
                self.inputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[0].abspath(),
            ]
        )

    def scan(self):
        return ([], [])


@feature('motor:preprocess')
@before_method('process_source')
def kernel_generate_ast(self):
    mak_node = self.bld.motornode.make_node('mak')
    for kernel, source, path, out in getattr(self, 'kernels', []) + getattr(self, 'kernels_cpu', []):
        out.parent.mkdir()
        self.source.append(out)

        tsk = self.create_task(
            'kernel_ast',
            [source],
            [out],
            kernel=self.bld.motornode.find_node('mak/tools/bin/kernel_ast.py'),
            kernel_name='.'.join(kernel),
            macros=self.bld.motornode.find_node('mak/libs/cpp/macros_ignore'),
            path=self.bld.variant_dir,
            dep_nodes=[mak_node.find_node('tools/bin/kernel_ast.py')] +
            mak_node.find_node('libs/cpp').ant_glob('**/*.py') + mak_node.find_node('libs/ply').ant_glob('**/*.py'),
        )
