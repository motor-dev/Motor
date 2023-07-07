/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_STREAM_FACTORY_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_STREAM_FACTORY_HH
#pragma once

#include <motor/scheduler/kernel/parameters/stream.factory.hh>

#include <motor/meta/class.meta.hh>
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
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(),
                                            u32(sizeof(KernelScheduler::Stream< T >)),
                                            motor_class< KernelScheduler::IStream >(),
                                            0,
                                            motor_class< KernelScheduler::IStream >()->objects,
                                            motor_class< KernelScheduler::IStream >()->tags,
                                            motor_class< KernelScheduler::IStream >()->properties,
                                            motor_class< KernelScheduler::IStream >()->methods,
                                            {nullptr},
                                            motor_class< KernelScheduler::IStream >()->operators,
                                            nullptr,
                                            nullptr};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(minitl::format< 2048u >("Stream<%s>") | TypeID< T >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta

#endif
