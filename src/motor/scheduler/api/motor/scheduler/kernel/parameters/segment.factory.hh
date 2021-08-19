/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENT_FACTORY_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_SEGMENT_FACTORY_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>

#include <motor/meta/classinfo.script.hh>
#include <motor/meta/engine/methodinfo.script.hh>
#include <motor/meta/engine/objectinfo.script.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor {

namespace KernelScheduler {
class IParameter;
template < typename T >
class Segment;
}  // namespace KernelScheduler

namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Segment< T > >
{
    static Value construct(Value* parameters, u32 parameterCount)
    {
        motor_assert(parameterCount == 0, "too many parameters");
        motor_forceuse(parameters);
        return Value(ref< KernelScheduler::Segment< T > >::create(Arena::task()));
    }
    static const Meta::Method::Overload s_ctrOverload;
    static const Meta::Method           s_ctr;
    static Meta::ObjectInfo             s_productClass;
    static MOTOR_EXPORT KernelScheduler::IParameter::ParameterRegistration s_registration;

    static MOTOR_EXPORT raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class
            = {istring(minitl::format< 256u >("Segment<%s>") | motor_class< T >()->name),
               u32(sizeof(KernelScheduler::Segment< T >)),
               0,
               Meta::ClassType_Object,
               {0},
               motor_class< KernelScheduler::IParameter >(),
               {&s_productClass},
               {0},
               {0, 0},
               {1, &s_ctr},
               {&s_ctr},
               {0},
               0,
               0};
        raw< const Meta::Class > result = {&s_class};
        (void)s_registration;
        return result;
    }
};

template < typename T >
const Meta::Method::Overload ClassID< KernelScheduler::Segment< T > >::s_ctrOverload = {
    {0}, {0, 0}, motor_type< ref< KernelScheduler::Segment< T > > >(), false, {0, 0}, &construct};

template < typename T >
const Meta::Method ClassID< KernelScheduler::Segment< T > >::s_ctr
    = {Meta::Class::nameConstructor(),
       {1, &s_ctrOverload},
       {&ClassID< KernelScheduler::Segment< T > >::s_ctr}};

template < typename T >
Meta::ObjectInfo ClassID< KernelScheduler::Segment< T > >::s_productClass
    = {{0},
       {0},
       KernelScheduler::IParameter::getProductTypePropertyName(),
       Value(motor_type< ref< KernelScheduler::Product< KernelScheduler::Segment< T > > > >())};

template < typename T >
KernelScheduler::IParameter::ParameterRegistration
    ClassID< KernelScheduler::Segment< T > >::s_registration(klass());

}  // namespace Meta
}  // namespace Motor

/**************************************************************************************************/
#endif
