/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_KERNEL_META_HH
#define MOTOR_SCHEDULER_KERNEL_KERNEL_META_HH

#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.hh>
#include <motor/scheduler/kernel/code.meta.hh>

namespace Motor { namespace KernelScheduler {

enum SchedulerType
{
    CPUType,
    GPUType
};

class motor_api(SCHEDULER) Kernel : public Resource::Description< Kernel >
{
private:
    ref< const Code > m_kernelCode;
    const istring     m_name;

public:
    Kernel(const ref< const Code >& code, const istring& name);
    ~Kernel() override;

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

#include <motor/scheduler/kernel/kernel.meta.factory.hh>
#endif
