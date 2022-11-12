/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/plugin.compute.opencl/scheduler.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL_GL {

class Scheduler : public OpenCL::Scheduler
{
private:
    static minitl::array< cl_context_properties > createPlatformSpecificContextProperties();

public:
    Scheduler(const Plugin::Context& context);
    ~Scheduler();

public:
    void* operator new(size_t size, void* where)
    {
        return ::operator new(size, where);
    }
    void operator delete(void* memory, void* where)
    {
        ::operator delete(memory, where);
    }
    void operator delete(void* memory)
    {
        motor_notreached();
        ::operator delete(memory);
    }
};

}}}  // namespace Motor::KernelScheduler::OpenCL_GL
