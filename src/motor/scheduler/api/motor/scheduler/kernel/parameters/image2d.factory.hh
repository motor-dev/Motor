/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE2D_FACTORY_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_IMAGE2D_FACTORY_HH_
/**************************************************************************************************/
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
class Image2D;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Image2D< T > >
{
    static MOTOR_EXPORT raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(), u32(sizeof(KernelScheduler::Image2D< T >)),
                                            0,      Meta::ClassType_Object,
                                            {0},    motor_class< KernelScheduler::IImage2D >(),
                                            {0},    {0},
                                            {0, 0}, {0, 0},
                                            {0},    Meta::OperatorTable::s_emptyTable,
                                            0,      0};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    static MOTOR_EXPORT istring name()
    {
        static const istring s_name(minitl::format< 2048u >("Image2D<%s>") | TypeID< T >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
