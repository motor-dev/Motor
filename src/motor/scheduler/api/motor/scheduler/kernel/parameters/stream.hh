/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_STREAM_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_STREAM_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Stream : public IParameter
{
protected:
    ref< IProduct > makeProduct(ref< IParameter > parameter, weak< Task::ITask > task)
    {
        return ref< Product< Stream< T > > >::create(
            Arena::task(), motor_checked_cast< Stream< T > >(parameter), task);
    }

public:
    Stream()
    {
    }
    ~Stream()
    {
    }
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/stream.factory.hh>

/**************************************************************************************************/
#endif
