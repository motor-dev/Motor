/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENTS_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENTS_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/kernel/input/segments.hh>
#include <motor/minitl/typemanipulation.hh>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>
#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Segments : public IParameter
{
protected:
    ref< IProduct > makeProduct(ref< IParameter > parameter, weak< Task::ITask > task)
    {
        return ref< Product< Segments< T > > >::create(
            Arena::task(), motor_checked_cast< Segments< T > >(parameter), task);
    }

public:
    Segments()
    {
    }
    ~Segments()
    {
    }
};

template < typename T >
struct ParamTypeToKernelType< ::Kernel::segments< T > >
{
    typedef Segments< typename minitl::remove_const< T >::type > Type;
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/segments.factory.hh>

/**************************************************************************************************/
#endif
