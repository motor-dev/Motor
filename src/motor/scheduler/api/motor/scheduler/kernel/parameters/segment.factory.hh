/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENT_FACTORY_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENT_FACTORY_HH
#pragma once

#include <motor/scheduler/kernel/parameters/segment.hh>

#include <motor/meta/class.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace KernelScheduler {

class IParameter;
template < typename T >
class Segment;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Segment< T > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(),
                                            u32(sizeof(KernelScheduler::Segment< T >)),
                                            motor_class< KernelScheduler::ISegment >(),
                                            0,
                                            motor_class< KernelScheduler::ISegment >()->objects,
                                            motor_class< KernelScheduler::ISegment >()->tags,
                                            motor_class< KernelScheduler::ISegment >()->properties,
                                            motor_class< KernelScheduler::ISegment >()->methods,
                                            {nullptr},
                                            motor_class< KernelScheduler::ISegment >()->interfaces,
                                            nullptr,
                                            nullptr};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(minitl::format< 2048u >("Segment<%s>") | TypeID< T >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta

#endif
