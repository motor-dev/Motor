/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_KERNEL_SCRIPT_HH_
#define MOTOR_SCHEDULER_KERNEL_KERNEL_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.meta.hh>
#include <motor/scheduler/kernel/code.meta.hh>

namespace Motor { namespace KernelScheduler {

enum SchedulerType
{
    CPUType,
    GPUType
};

class motor_api(SCHEDULER) Kernel : public Resource::Description
{
private:
    ref< const Code > m_kernelCode;
    const istring     m_name;

public:
    Kernel(ref< const Code > code, const istring& name);
    ~Kernel();

    istring name() const
    {
        return m_name;
    }
    weak< const Code > code() const
    {
        return m_kernelCode;
    }
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
