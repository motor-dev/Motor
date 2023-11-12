/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_CPU_CODEOBJECT_HH
#define MOTOR_PLUGIN_COMPUTE_CPU_CODEOBJECT_HH

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/plugin/dynobject.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class KernelObject;

class CodeObject : public minitl::pointer
{
    friend class KernelObject;

private:
    Plugin::DynamicObject m_kernel;

public:
    explicit CodeObject(const inamespace& name);
    ~CodeObject() override;
};

}}}  // namespace Motor::KernelScheduler::CPU

#endif
