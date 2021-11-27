/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE1D_FACTORY_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE1D_FACTORY_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor {

namespace KernelScheduler {
class IParameter;
template < typename T >
class Image1D;
}  // namespace KernelScheduler

namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Image1D< T > >
{
    static Value construct(raw< const Meta::Method > method, Value* parameters, u32 parameterCount)
    {
        motor_forceuse(method);
        motor_assert(parameterCount == 0, "too many parameters");
        motor_forceuse(parameters);
        return Value(ref< KernelScheduler::Image1D< T > >::create(Arena::task()));
    }
    static const Meta::Method::Overload s_ctrOverload;
    static const Meta::Method           s_ctr;
    static MOTOR_EXPORT KernelScheduler::IParameter::ParameterRegistration s_registration;

    static MOTOR_EXPORT raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class
            = {istring(minitl::format< 256u >("Image1D<%s>") | motor_class< T >()->name),
               u32(sizeof(KernelScheduler::Image1D< T >)),
               0,
               Meta::ClassType_Object,
               {0},
               motor_class< KernelScheduler::IParameter >(),
               {0},
               {0},
               {0, 0},
               {1, &s_ctr},
               {&s_ctr},
               Meta::OperatorTable::s_emptyTable,
               0,
               0};
        raw< const Meta::Class > result = {&s_class};
        (void)s_registration;
        return result;
    }
};

template < typename T >
const Meta::Method::Overload ClassID< KernelScheduler::Image1D< T > >::s_ctrOverload
    = {{0}, {0, 0}, motor_type< ref< KernelScheduler::Image1D< T > > >(), false, &construct};

template < typename T >
const Meta::Method ClassID< KernelScheduler::Image1D< T > >::s_ctr
    = {Meta::Class::nameConstructor(),
       {1, &s_ctrOverload},
       {&ClassID< KernelScheduler::Image1D< T > >::s_ctr}};

template < typename T >
KernelScheduler::IParameter::ParameterRegistration
    ClassID< KernelScheduler::Image1D< T > >::s_registration(klass());

}  // namespace Meta
}  // namespace Motor

/**************************************************************************************************/
#endif
