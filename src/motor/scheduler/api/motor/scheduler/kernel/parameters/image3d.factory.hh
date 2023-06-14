/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE3D_FACTORY_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_IMAGE3D_FACTORY_HH

#include <motor/scheduler/kernel/parameters/image3d.hh>

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
        static const Meta::Class s_class = {name(),
                                            u32(sizeof(KernelScheduler::Image3D< T >)),
                                            0,
                                            Meta::ClassType_Object,
                                            {nullptr},
                                            motor_class< KernelScheduler::IImage3D >(),
                                            {nullptr},
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
        static const istring s_name(minitl::format< 2048u >("Image3D<%s>") | TypeID< T >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta

#endif
