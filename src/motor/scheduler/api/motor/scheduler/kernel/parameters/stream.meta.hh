/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_STREAM_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_STREAM_HH

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

#include <motor/scheduler/kernel/product.meta.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Stream : public IStream
{
private:
    MOTOR_EXPORT static IStream::ParameterRegistration s_registration;

public:
    Stream()
    {
        motor_forceuse(s_registration);
    }
    ~Stream() override = default;
};

/*
template < typename T >
IStream::ParameterRegistration Stream< T >::s_registration(motor_class< T >(),
                                                           motor_class< Stream< T > >());
*/

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/stream.meta.factory.hh>

#endif
