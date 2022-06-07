/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENT_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENT_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/parameters/parametertype.hh>

#include <motor/kernel/input/segment.hh>
#include <motor/minitl/type_traits.hh>
#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Segment : public ISegment
{
private:
    static MOTOR_EXPORT ISegment::ParameterRegistration s_registration;

public:
    Segment()
    {
        (void)s_registration;
    }
    ~Segment()
    {
    }
};

template < typename T >
ISegment::ParameterRegistration Segment< T >::s_registration(motor_class< T >(),
                                                             motor_class< Segment< T > >());

template < typename T >
struct ParamTypeToKernelType< ::Kernel::segment< T > >
{
    typedef Segment< minitl::remove_const_t< T > > Type;
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/segment.factory.hh>

/**************************************************************************************************/
#endif
