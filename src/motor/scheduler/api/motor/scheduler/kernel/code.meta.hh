/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_CODE_META_HH
#define MOTOR_SCHEDULER_KERNEL_CODE_META_HH

#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) Code : public Resource::Description< Code >
{
protected:
    const inamespace m_name;

public:
    explicit Code(const inamespace& name);
    ~Code() override;

    inamespace name() const
    {
        return m_name;
    }
};

}}  // namespace Motor::KernelScheduler

#endif
