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
class Image3D : public IParameter
{
public:
    Image3D()
    {
    }
    ~Image3D()
    {
    }
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image3d.factory.hh>

/**************************************************************************************************/
#endif
