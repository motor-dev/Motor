/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Stream : public IStream
{
private:
    MOTOR_EXPORT static IStream::ParameterRegistration s_registration;

public:
    Stream()
    {
        (void)s_registration;
    }
    ~Stream()
    {
    }
};

template < typename T >
IStream::ParameterRegistration Stream< T >::s_registration(motor_class< T >(),
                                                           motor_class< Stream< T > >());

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/stream.factory.hh>
