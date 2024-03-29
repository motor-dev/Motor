/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE2D_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE2D_HH

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/parameters/parametertype.hh>

#include <motor/scheduler/kernel/product.meta.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Image2D : public IImage2D
{
private:
    MOTOR_EXPORT static IImage2D::ParameterRegistration s_registration;

public:
    Image2D()
    {
        (void)s_registration;
    }
    ~Image2D() override = default;
};

/*
template < typename T >
IImage2D::ParameterRegistration Image2D< T >::s_registration(motor_class< T >(),
                                                             motor_class< Image2D< T > >());
*/

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image2d.meta.factory.hh>

#endif
