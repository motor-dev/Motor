/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE1D_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE1D_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>

#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Image1D : public IParameter
{
protected:
    ref< IProduct > makeProduct(ref< IParameter > parameter, weak< Task::ITask > task)
    {
        return ref< Product< Image1D< T > > >::create(
            Arena::task(), motor_checked_cast< Image1D< T > >(parameter), task);
    }

public:
    Image1D()
    {
    }
    ~Image1D()
    {
    }
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image1d.factory.hh>

/**************************************************************************************************/
#endif
