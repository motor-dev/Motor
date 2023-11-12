/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_IMEMORYHOST_HH
#define MOTOR_SCHEDULER_KERNEL_IMEMORYHOST_HH

#include <motor/scheduler/stdafx.h>

namespace Motor { namespace KernelScheduler {

class IMemoryBuffer;

class motor_api(SCHEDULER) IMemoryHost : public minitl::pointer
{
    friend class IMemoryBuffer;

protected:
    const istring m_name;

protected:
    explicit IMemoryHost(const istring& name);
    ~IMemoryHost() override;

    virtual void release(const weak< IMemoryBuffer >& buffer) = 0;
};

}}  // namespace Motor::KernelScheduler

#endif
