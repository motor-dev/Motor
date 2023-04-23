/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) IMemoryBuffer : public minitl::refcountable
{
protected:
    weak< const IMemoryHost > const m_host;

protected:
    explicit IMemoryBuffer(const weak< const IMemoryHost >& host);
    ~IMemoryBuffer() override;

public:
    weak< const IMemoryHost > getHost() const
    {
        return m_host;
    }
};

}}  // namespace Motor::KernelScheduler
