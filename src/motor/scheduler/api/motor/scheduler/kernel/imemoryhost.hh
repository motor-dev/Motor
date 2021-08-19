/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_IMEMORYHOST_HH_
#define MOTOR_SCHEDULER_KERNEL_IMEMORYHOST_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.script.hh>

namespace Motor { namespace KernelScheduler {

class IMemoryBuffer;

class motor_api(SCHEDULER) IMemoryHost : public minitl::refcountable
{
    friend class IMemoryBuffer;

protected:
    const istring m_name;

protected:
    IMemoryHost(const istring& name);
    ~IMemoryHost();

    virtual void release(weak< IMemoryBuffer > buffer) = 0;
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
