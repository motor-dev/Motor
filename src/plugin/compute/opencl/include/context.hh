/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_OPENCL_CONTEXT_HH
#define MOTOR_PLUGIN_COMPUTE_OPENCL_CONTEXT_HH

#include <motor/plugin.compute.opencl/stdafx.h>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class Platform;
class Scheduler;

class Context : public minitl::refcountable
{
    friend class Scheduler;

private:
    const weak< Platform > m_platform;
    cl_device_id           m_device;
    cl_context             m_context;
    const u32              m_pointerSize;

public:
    Context(const weak< Platform >& platform, cl_device_id device, cl_context context);
    ~Context() override;

    inline u32 getPointerSize() const
    {
        return m_pointerSize;
    }

    cl_program buildProgram(u64 size, const char* code) const;
};

}}}  // namespace Motor::KernelScheduler::OpenCL

#endif
