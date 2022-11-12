/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/plugin/dynobject.hh>
#include <motor/scheduler/task/task.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class KernelObject;

class CodeObject : public minitl::refcountable
{
    friend class KernelObject;

private:
    Plugin::DynamicObject m_kernel;

public:
    CodeObject(const inamespace& name);
    ~CodeObject();
};

}}}  // namespace Motor::KernelScheduler::CPU
