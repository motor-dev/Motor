/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace KernelScheduler {

class IParameter;
template < typename T >
class Image3D;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Image3D< T > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(), u32(sizeof(KernelScheduler::Image3D< T >)),
                                            0,      Meta::ClassType_Object,
                                            {0},    motor_class< KernelScheduler::IImage3D >(),
                                            {0},    {0},
                                            {0, 0}, {0, 0},
                                            {0},    Meta::OperatorTable::s_emptyTable,
                                            0,      0};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(minitl::format< 2048u >("Image3D<%s>") | TypeID< T >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta
