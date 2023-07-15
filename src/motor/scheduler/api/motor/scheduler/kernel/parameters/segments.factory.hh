/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENTS_FACTORY_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENTS_FACTORY_HH
#pragma once

#include <motor/scheduler/kernel/parameters/segments.hh>

#include <motor/meta/class.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace KernelScheduler {

class IParameter;
template < typename T >
class Segments;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Segments< T > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static Meta::Object s_productClass = {
            motor_class< KernelScheduler::ISegments >()->objects,
            {nullptr},
            KernelScheduler::IParameter::getProductTypePropertyName(),
            Meta::Value(
                motor_class< KernelScheduler::Product<
                    KernelScheduler::Segments< typename minitl::remove_const< T >::type > > >())};

        static Meta::Object s_parameterClassProperty
            = {{&s_productClass},
               {nullptr},
               istring("ParameterClass"),
               Meta::Value(motor_class< typename minitl::remove_const< T >::type >())};

        static const Meta::Class s_class = {name(),
                                            u32(sizeof(KernelScheduler::Segments< T >)),
                                            motor_class< KernelScheduler::ISegments >(),
                                            0,
                                            {&s_parameterClassProperty},
                                            motor_class< KernelScheduler::ISegments >()->tags,
                                            motor_class< KernelScheduler::ISegments >()->properties,
                                            motor_class< KernelScheduler::ISegments >()->methods,
                                            {nullptr},
                                            motor_class< KernelScheduler::ISegments >()->interfaces,
                                            nullptr,
                                            nullptr};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("Segments<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

}}  // namespace Motor::Meta

#endif
