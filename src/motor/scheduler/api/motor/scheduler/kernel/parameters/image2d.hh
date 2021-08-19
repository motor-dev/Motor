/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE2D_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE2D_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>

#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Image2D : public IParameter
{
protected:
    ref< IProduct > makeProduct(ref< IParameter > parameter, weak< Task::ITask > task)
    {
        return ref< Product< Image2D< T > > >::create(
            Arena::task(), motor_checked_cast< Image2D< T > >(parameter), task);
    }

public:
    Image2D()
    {
    }
    ~Image2D()
    {
    }
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image2d.factory.hh>

/**************************************************************************************************/
#endif
