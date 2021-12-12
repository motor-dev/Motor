#!/usr/bin/env python
# encoding: utf-8

from waflib import Task
from waflib.TaskGen import extension
try:
    import cPickle as pickle
except ImportError:
    import pickle

TEMPLATE_CLASS_H = """
%(Namespace)s

class %(KernelName)sKernel : public ::Motor::KernelScheduler::Producer
{
private:
    %(argument_field)s

private:
    typedef ::Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Kernel > ResourceHook;
    typedef ::Motor::Plugin::PluginHook< ResourceHook > PluginHook;
    static MOTOR_EXPORT PluginHook g_kernelHook;

    virtual ref< ::Motor::KernelScheduler::Producer::Runtime > createRuntime(
        weak< const ::Motor::KernelScheduler::ProducerLoader > loader
    ) const override;

published:
    %(argument_outs)s
    %(KernelName)sKernel(%(argument_params)s);
    ~%(KernelName)sKernel();
};

%(end_Namespace)s

"""

TEMPLATE_H = """
/* Motor <motor.devel@gmail.com> / 2008-2015
   see LICENSE for detail */
#ifndef MOTOR_%(PLUGIN)s_%(NAME)s_META_HH_
#define MOTOR_%(PLUGIN)s_%(NAME)s_META_HH_
/**************************************************************************************************/
%(pch)s
#include    <motor/scheduler/kernel/kernel.meta.hh>
#include    <motor/scheduler/task/itask.hh>
#include    <motor/scheduler/kernel/product.hh>
#include    <motor/scheduler/kernel/producer.meta.hh>
#include    <motor/scheduler/kernel/producerloader.hh>
#include    <motor/scheduler/kernel/parameters/parameters.hh>
#include    <motor/scheduler/task/kerneltask.hh>
#include    <motor/kernel/colors.hh>
#include    <motor/plugin/resourcehook.hh>
%(includes)s
%(usings)s

%(Tasks_H)s


/**************************************************************************************************/
#endif
"""

TEMPLATE_CLASS_CC = """
%(Namespace)s

static ref< ::Motor::KernelScheduler::Kernel > s_%(Name)sKernel%(KernelName)s = ref< ::Motor::KernelScheduler::Kernel >::create(::Motor::Arena::task(), s_%(Name)sKernelCode, ::Motor::istring("%(kernelName)s"));

%(KernelName)sKernel::PluginHook %(KernelName)sKernel::g_kernelHook = %(KernelName)sKernel::PluginHook(::Motor::MOTOR_CONCAT(g_pluginHooks_, MOTOR_PROJECTID), %(KernelName)sKernel::ResourceHook(s_%(Name)sKernel%(KernelName)s));

%(KernelName)sKernel::%(KernelName)sKernel(%(argument_params)s)
    :   %(argument_assign)s
{
}

%(KernelName)sKernel::~%(KernelName)sKernel()
{
}

ref< ::Motor::KernelScheduler::Producer::Runtime > %(KernelName)sKernel::createRuntime(
    weak< const ::Motor::KernelScheduler::ProducerLoader > loader
) const
{
    motor_forceuse(loader);
    void* memory = malloca(sizeof(ref< ::Motor::KernelScheduler::IParameter >) * %(argument_count)s);
    ref< ::Motor::KernelScheduler::IParameter >* parameters = reinterpret_cast<ref< ::Motor::KernelScheduler::IParameter >*>(memory);
    %(parameter_assign)s
    ref< ::Motor::Task::KernelTask > task = ref< ::Motor::Task::KernelTask >::create(
            ::Motor::Arena::task(),
            "%(kernel_full_name)s.%(KernelName)s",
            Motor::KernelScheduler::GPUType,
            Motor::Colors::Red::Red,
            Motor::Scheduler::High,
            s_%(Name)sKernel%(KernelName)s,
            parameters, parameters + %(argument_count)s
        );
    ref< ::Motor::KernelScheduler::Producer::Runtime > result = ref< ::Motor::KernelScheduler::Producer::Runtime >::create(::Motor::Arena::task(), task, %(argument_count)s);
    %(parameter_save)s
    %(product_chain)s
    for (u32 i = 0; i < %(argument_count)s; ++i)
        parameters[i].~ref();
    freea(memory);
    return result;
}

%(end_Namespace)s
"""

TEMPLATE_CC = """
%(pch)s
#include "%(header)s"


namespace Motor
{

extern Plugin::HookList MOTOR_CONCAT(g_pluginHooks_, MOTOR_PROJECTID);

}


static ref< ::Motor::KernelScheduler::Code > s_%(Name)sKernelCode = ref< ::Motor::KernelScheduler::Code >::create(::Motor::Arena::task(), ::Motor::inamespace("%(plugin)s.%(kernel_full_name)s"));
MOTOR_EXPORT ::Motor::Plugin::PluginHook< Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Code > > g_%(Name)sKernelHook = ::Motor::Plugin::PluginHook< ::Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Code > >(::Motor::MOTOR_CONCAT(g_pluginHooks_, MOTOR_PROJECTID), ::Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Code >(s_%(Name)sKernelCode));

%(Tasks_CC)s

"""


def underscore_to_camelcase(value):
    return ''.join(x.capitalize() or '_' for x in value.split('_'))


class kernel_task(Task.Task):
    color = 'CYAN'

    def sig_vars(self):
        self.m.update(TEMPLATE_CLASS_CC.encode('utf-8'))
        self.m.update(TEMPLATE_CC.encode('utf-8'))
        self.m.update(TEMPLATE_CLASS_H.encode('utf-8'))
        self.m.update(TEMPLATE_H.encode('utf-8'))

    def scan(self):
        return ([], [])

    def run(self):
        with open(self.inputs[0].abspath(), 'rb') as input_file:
            kernel_name, includes, source, kernel_methods = pickle.load(input_file)

        kernel_namespace = ['Kernels'] + kernel_name.split('.')
        kernel_name = kernel_namespace[-1]
        kernel_full_name = kernel_namespace[1:]

        params = {
            'header': self.outputs[1].path_from(self.generator.bld.srcnode),
            'Namespace': ' { '.join('namespace %s' % n.capitalize() for n in kernel_namespace[:-1]) + '\n{\n',
            'end_Namespace': '}' * (len(kernel_namespace) - 1),
            'name': kernel_name,
            'Name': kernel_name.capitalize(),
            'NAME': kernel_name.upper(),
            'kernel_full_name': '.'.join(kernel_full_name),
            'pch': '#include <%s>\n' % self.generator.pchstop if self.generator.pchstop else '',
            'PLUGIN': self.generator.env.PLUGIN.upper(),
            'module': self.generator.env.PLUGIN,
            'plugin': self.generator.env.PLUGIN.replace('_', '.'),
            'includes': '\n'.join(includes[0]),
            'usings': '\n'.join(['using namespace %s;' % u for u in includes[1]]),
        }
        tasks_cc = []
        tasks_h = []
        for method, namespace, args in kernel_methods:
            argument_assign = '\n    ,   '.join(
                tuple('m_%s(%s)' % (arg[0], arg[0]) for arg in args) + tuple(
                    '%s(ref< const Motor::KernelScheduler::Product< Motor::KernelScheduler::ParamTypeToKernelType< %s >::Type > >::create(Motor::Arena::task(), this))'
                    % (arg[0], arg[1]) for arg in args
                )
            )

            task_params = {
                'Namespace':
                    ' '.join('namespace %s {' % n for n in namespace),
                'end_Namespace':
                    '}' * len(namespace),
                'Name':
                    kernel_name.capitalize(),
                'kernel_full_name':
                    '.'.join(kernel_full_name),
                'kernelName':
                    method.name,
                'KernelName':
                    underscore_to_camelcase(method.name),
                'argument_count':
                    len(args),
                'argument_field':
                    '\n    '.join(
                        (
                            'weak< const ::Motor::KernelScheduler::Product< ::Motor::KernelScheduler::ParamTypeToKernelType< %s >::Type > > const m_%s;'
                            % (arg[1], arg[0]) for arg in args
                        )
                    ),
                'argument_result_assign':
                    '\n    '.join(('result[%d] = m_%s->parameter();' % (i, arg[0]) for i, arg in enumerate(args))),
                'argument_outs':
                    '\n    '.join(
                        (
                            'ref< const ::Motor::KernelScheduler::Product< ::Motor::KernelScheduler::ParamTypeToKernelType< %s >::Type > > const %s;'
                            % (arg[1], arg[0]) for arg in args
                        )
                    ),
                'argument_params':
                    ', '.join(
                        (
                            'weak< const ::Motor::KernelScheduler::Product< ::Motor::KernelScheduler::ParamTypeToKernelType< %s >::Type > > %s'
                            % (arg[1], arg[0]) for arg in args
                        )
                    ),
                'argument_assign':
                    argument_assign,
                'parameter_assign':
                    '    \n'.join(
                        [
                            'new(&parameters[%d]) ref< ::Motor::KernelScheduler::IParameter >(m_%s->producer()->getParameter(loader, m_%s));'
                            % (i, arg[0], arg[0]) for i, arg in enumerate(args)
                        ]
                    ),
                'parameter_save':
                    '    \n'.join(
                        [
                            'result->parameters[%d] = minitl::make_tuple(%s, parameters[%d]);' % (i, arg[0], i)
                            for i, arg in enumerate(args)
                        ]
                    ),
                'product_chain':
                    '    \n'.join(
                        [
                            'result->chain.push_back(::Motor::Task::ITask::CallbackConnection(\n'
                            '        m_%s->producer()->getTask(loader),\n'
                            '        task->startCallback())\n'
                            '    );' % arg[0] for arg in args
                        ]
                    )
            }
            tasks_cc.append(TEMPLATE_CLASS_CC % task_params)
            tasks_h.append(TEMPLATE_CLASS_H % task_params)

        params['Tasks_CC'] = '\n\n'.join(tasks_cc)
        params['Tasks_H'] = '\n\n'.join(tasks_h)
        with open(self.outputs[0].abspath(), 'w') as out:
            out.write(TEMPLATE_CC % params)
        with open(self.outputs[1].abspath(), 'w') as out:
            out.write(TEMPLATE_H % params)


@extension('.ast')
def kernel_generate(task_gen, ast_node):
    outs = [ast_node.change_ext('task.cc'), ast_node.change_ext('task.meta.hh')]
    task = task_gen.create_task('kernel_task', [ast_node], outs)
    try:
        task_gen.out_sources.append(outs[0])
    except AttributeError:
        task_gen.out_sources = [outs[0]]
    task_gen.source.append(outs[1])
