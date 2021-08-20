/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENT_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENT_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/kernel/input/segment.hh>
#include <motor/minitl/typemanipulation.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Segment : public IParameter
{
protected:
    ref< IProduct > makeProduct(ref< IParameter > parameter, weak< Task::ITask > task)
    {
        return ref< Product< Segment< T > > >::create(
            Arena::task(), motor_checked_cast< Segment< T > >(parameter), task);
    }

public:
    Segment()
    {
    }
    ~Segment()
    {
    }
};

template < typename T >
struct ParamTypeToKernelType< ::Kernel::segment< T > >
{
    typedef Segment< typename minitl::remove_const< T >::type > Type;
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/segment.factory.hh>

/**************************************************************************************************/
#endif
