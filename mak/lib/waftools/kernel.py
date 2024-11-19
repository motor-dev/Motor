import os
import sys
import build_framework
import waflib.Build
import waflib.Task
import waflib.TaskGen
import waflib.Node


class kernel(waflib.Task.Task):
    color = 'CYAN'

    def run(self) -> int:
        kernel_node = getattr(self, 'kernel')  # type: waflib.Node.Node
        macros = getattr(self, 'macros')  # type: waflib.Node.Node
        kernel_name = getattr(self, 'kernel_name')  # type: str

        return self.exec_command(
            [
                sys.executable,
                kernel_node.abspath(),
                '-x',
                'c++',
                '--std',
                'c++14',
                '-D',
                macros.abspath(),
                '--name',
                kernel_name,
                '--tmp',
                self.generator.bld.bldnode.abspath(),
                '--module',
                getattr(self.generator, 'parent'),
                self.inputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[0].path_from(self.generator.bld.bldnode),
                self.outputs[1].path_from(self.generator.bld.bldnode),
                self.outputs[2].path_from(self.generator.bld.bldnode),
                self.outputs[2].path_from(getattr(self.generator, 'generated_include_node')).replace('\\', '/'),
            ]
        )


@waflib.TaskGen.feature('motor:preprocess')
@waflib.TaskGen.before_method('process_source')
def generate_kernel(task_gen: waflib.TaskGen.task_gen) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    kernel_list = getattr(task_gen, 'kernels', [])
    if kernel_list:
        mak_node = task_gen.bld.motornode.make_node('mak')
        dep_nodes = [mak_node.make_node('bin/kernel.py')]
        kernel_node = mak_node.make_node('bin/kernel.py')
        macros_node = mak_node.make_node('tools/macros_def.json')

        for kernel_name, source in kernel_list:
            out = build_framework.make_bld_node(task_gen, 'src/kernels', None,
                                                '%s.kernel' % (os.path.join(*kernel_name)))
            cc = out.change_ext('-kerneltask.cc')
            hh = build_framework.make_bld_node(task_gen, 'include/kernels', None,
                                               '%s-kerneltask.meta.hh' % (os.path.join(*kernel_name)))
            out.parent.mkdir()
            hh.parent.mkdir()

            task = task_gen.create_task(
                'kernel',
                [source],
                [out, cc, hh],
                kernel=kernel_node,
                macros=macros_node,
                cpu=os.path.splitext(source.name)[1] in ('.cc', '.cpp'),
                kernel_name='.'.join(kernel_name),
            )
            task.dep_nodes = task_gen.bld.pyxx_nodes + dep_nodes

            task_gen.source.append(hh)
            getattr(task_gen, 'out_sources').append(cc)


@waflib.TaskGen.feature('motor:cxx')
@waflib.TaskGen.before_method('process_source')
def process_kernels(task_gen: waflib.TaskGen.task_gen) -> None:
    assert isinstance(task_gen.bld, build_framework.BuildContext)
    preprocess = getattr(task_gen, 'preprocess', None)
    kernel_list = getattr(preprocess, 'kernels', [])
    for kernel_name, source in kernel_list:
        assert preprocess is not None
        kernel_node = build_framework.make_bld_node(preprocess, 'src/kernels', None,
                                                    '%s.kernel' % (os.path.join(*kernel_name)))
        for kernel_processor in task_gen.bld.kernel_processors:
            kernel_processor(task_gen.bld, task_gen, kernel_name, source, kernel_node,
                             source.name.endswith('.cl') and 'gpu' or 'cpu')


def build(_: waflib.Build.BuildContext) -> None:
    pass
