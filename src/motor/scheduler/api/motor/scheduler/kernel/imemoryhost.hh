/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>

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

#include <motor/scheduler/kernel/imemorybuffer.hh>
