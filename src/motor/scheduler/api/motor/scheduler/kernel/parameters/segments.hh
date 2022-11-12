/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/parameters/parametertype.hh>

#include <motor/kernel/input/segments.hh>
#include <motor/minitl/type_traits.hh>
#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Segments : public ISegments
{
private:
    MOTOR_EXPORT static ISegments::ParameterRegistration s_registration;

public:
    Segments()
    {
        (void)s_registration;
    }
    ~Segments()
    {
    }
};

template < typename T >
ISegments::ParameterRegistration Segments< T >::s_registration(motor_class< T >(),
                                                               motor_class< Segments< T > >());

template < typename T >
struct ParamTypeToKernelType< ::knl::segments< T > >
{
    typedef Segments< minitl::remove_const_t< T > > Type;
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/segments.factory.hh>
