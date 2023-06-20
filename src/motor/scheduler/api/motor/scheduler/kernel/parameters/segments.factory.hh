/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENTS_FACTORY_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_SEGMENTS_FACTORY_HH
#pragma once

#include <motor/scheduler/kernel/parameters/segments.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
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
        static Meta::ObjectInfo s_productClass = {
            {nullptr},
            {nullptr},
            KernelScheduler::IParameter::getProductTypePropertyName(),
            Meta::Value(
                motor_class< KernelScheduler::Product<
                    KernelScheduler::Segments< typename minitl::remove_const< T >::type > > >())};

        static Meta::ObjectInfo s_parameterClassProperty
            = {{&s_productClass},
               {nullptr},
               istring("ParameterClass"),
               Meta::Value(motor_class< typename minitl::remove_const< T >::type >())};

        static const Meta::Class s_class = {name(),
                                            u32(sizeof(KernelScheduler::Segments< T >)),
                                            0,
                                            Meta::ClassType_Object,
                                            {nullptr},
                                            motor_class< KernelScheduler::ISegments >(),
                                            {&s_parameterClassProperty},
                                            {nullptr},
                                            {0, nullptr},
                                            {0, nullptr},
                                            {nullptr},
                                            Meta::OperatorTable::s_emptyTable,
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
