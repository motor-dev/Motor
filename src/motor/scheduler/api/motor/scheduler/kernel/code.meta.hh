/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_CODE_META_HH_
#define MOTOR_SCHEDULER_KERNEL_CODE_META_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) Code : public Resource::Description< Code >
{
protected:
    const inamespace m_name;

public:
    Code(const inamespace& name);
    ~Code();

    inamespace name() const
    {
        return m_name;
    }
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
