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


def create_project_kernels(task_gen, kernel_name, kernel_source, kernel_node, kernel_type):
    if task_gen.env.PROJECTS:
        tgen = task_gen.bld.get_tgen_by_name(task_gen.name)
        target_suffix = '.'.join([kernel_type])
        env = task_gen.env
        kernel_target = task_gen.target_name + '.' + '.'.join(kernel_name) + '.cpu'
        kernel_task_gen = task_gen.bld(
            env=task_gen.env.derive(),
            bld_env=env,
            target=env.ENV_PREFIX % kernel_target,
            target_name=task_gen.name,
            safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
            source=[kernel_source],
            kernel_name=kernel_name,
            kernel_node=kernel_node,
            features=[
                'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel'
            ],
            defines=tgen.defines + [
                'MOTOR_KERNEL_ID=%s_%s' % (task_gen.target_name.replace('.', '_'), kernel_target.replace('.', '_')),
                'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                'MOTOR_KERNEL_TARGET=%s' % kernel_type
            ],
            includes=tgen.includes + [task_gen.bld.srcnode],
            use=[tgen.target] + tgen.use + [env.ENV_PREFIX % 'plugin.compute.cpu'],
            uselib=tgen.uselib,
            source_nodes=[('', kernel_source)]
        )
        kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name
        if kernel_type == 'gpu':
            kernel_target = task_gen.target_name + '.' + '.'.join(kernel_name) + '.cl'
            kernel_task_gen = task_gen.bld(
                env=task_gen.env.derive(),
                bld_env=env,
                target=env.ENV_PREFIX % kernel_target,
                target_name=task_gen.name,
                safe_target_name=kernel_target.replace('.', '_').replace('-', '_'),
                source=[kernel_source],
                kernel_name=kernel_name,
                kernel_node=kernel_node,
                features=[
                    'cxx', task_gen.bld.env.STATIC and 'cxxobjects' or 'cxxshlib', 'motor:cxx', 'motor:kernel'
                ],
                defines=tgen.defines + [
                    'MOTOR_KERNEL_ID=%s_%s' % (task_gen.target_name.replace('.', '_'), kernel_target.replace('.', '_')),
                    'MOTOR_KERNEL_NAME=%s' % (kernel_target),
                    'MOTOR_KERNEL_TARGET=%s' % kernel_type
                ],
                includes=tgen.includes + [task_gen.bld.srcnode] + env.CLC_KERNEL_HEADER_PATH,
                use=[tgen.target] + tgen.use + [env.ENV_PREFIX % 'plugin.compute.cl'],
                uselib=tgen.uselib,
                source_nodes=[('', kernel_source)]
            )
            kernel_task_gen.env.PLUGIN = task_gen.env.plugin_name


def build(build_context):
    task_gen.kernel_processors = [create_project_kernels]
