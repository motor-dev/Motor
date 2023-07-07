/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE2D_FACTORY_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE2D_FACTORY_HH
#pragma once

#include <motor/scheduler/kernel/parameters/image2d.hh>

#include <motor/meta/class.meta.hh>
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
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(),
                                            u32(sizeof(KernelScheduler::Image2D< T >)),
                                            motor_class< KernelScheduler::IImage2D >(),
                                            0,
                                            motor_class< KernelScheduler::IImage2D >()->objects,
                                            motor_class< KernelScheduler::IImage2D >()->tags,
                                            motor_class< KernelScheduler::IImage2D >()->properties,
                                            motor_class< KernelScheduler::IImage2D >()->methods,
                                            {nullptr},
                                            motor_class< KernelScheduler::IImage2D >()->operators,
                                            nullptr,
                                            nullptr};
        raw< const Meta::Class > result  = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(minitl::format< 2048u >("Image2D<%s>") | TypeID< T >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta

#endif
