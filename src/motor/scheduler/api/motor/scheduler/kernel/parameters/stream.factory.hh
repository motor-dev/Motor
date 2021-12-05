/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_STREAM_FACTORY_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_STREAM_FACTORY_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace KernelScheduler {

class IParameter;
template < typename T >
class Stream;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Stream< T > >
{
    static MOTOR_EXPORT raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class
            = {istring(minitl::format< 256u >("Stream<%s>") | motor_class< T >()->name),
               u32(sizeof(KernelScheduler::Stream< T >)),
               0,
               Meta::ClassType_Object,
               {0},
               motor_class< KernelScheduler::IStream >(),
               {0},
               {0},
               {0, 0},
               {0, 0},
               {0},
               Meta::OperatorTable::s_emptyTable,
               0,
               0};
        raw< const Meta::Class > result = {&s_class};
        return result;
    }
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
