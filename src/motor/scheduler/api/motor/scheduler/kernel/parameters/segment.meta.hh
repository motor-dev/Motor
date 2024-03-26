/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENT_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENT_HH

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/parameters/parametertype.hh>

#include <motor/kernel/input/segment.hh>
#include <motor/minitl/type_traits.hh>
#include <motor/scheduler/kernel/product.meta.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Segment : public ISegment
{
private:
    MOTOR_EXPORT static ISegment::ParameterRegistration s_registration;

public:
    Segment()
    {
        motor_forceuse(s_registration);
    }
    ~Segment() override = default;
};

/*
template < typename T >
ISegment::ParameterRegistration Segment< T >::s_registration(motor_class< T >(),
                                                             motor_class< Segment< T > >());
*/

template < typename T >
struct ParamTypeToKernelType< ::knl::segment< T > >
{
    typedef Segment< minitl::remove_const_t< T > > Type;
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/segment.meta.factory.hh>

#endif
