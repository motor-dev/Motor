/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE3D_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE3D_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/parameters/parametertype.hh>

#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Image3D : public IImage3D
{
private:
    static MOTOR_EXPORT IImage3D::ParameterRegistration s_registration;

public:
    Image3D()
    {
        (void)s_registration;
    }
    ~Image3D()
    {
    }
};

template < typename T >
IImage3D::ParameterRegistration Image3D< T >::s_registration(motor_class< T >(),
                                                             motor_class< Image3D< T > >());

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image3d.factory.hh>

/**************************************************************************************************/
#endif
