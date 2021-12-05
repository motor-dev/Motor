/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE2D_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE2D_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/parameters/parametertype.hh>

#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Image2D : public IImage2D
{
private:
    static MOTOR_EXPORT IImage2D::ParameterRegistration s_registration;

public:
    Image2D()
    {
        (void)s_registration;
    }
    ~Image2D()
    {
    }
};

template < typename T >
IImage2D::ParameterRegistration Image2D< T >::s_registration(motor_class< T >(),
                                                             motor_class< Image2D< T > >());

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image2d.factory.hh>

/**************************************************************************************************/
#endif
