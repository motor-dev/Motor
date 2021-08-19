/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PRODUCT_FACTORY_HH_
#define MOTOR_SCHEDULER_KERNEL_PRODUCT_FACTORY_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/iproduct.script.hh>

#include <motor/meta/classinfo.script.hh>
#include <motor/meta/engine/objectinfo.script.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor {

namespace KernelScheduler {

template < typename T >
class Product;
}  // namespace KernelScheduler

namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Product< T > >
{
    static MOTOR_EXPORT raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class
            = {istring(minitl::format< 256u >("Product<%s>") | motor_class< T >()->name),
               u32(sizeof(KernelScheduler::Product< T >)),
               0,
               Meta::ClassType_Object,
               {KernelScheduler::IProduct::getNamespace().m_ptr},
               {motor_class< KernelScheduler::IProduct >().m_ptr},
               {0},
               {0},
               {0, 0},
               {0, 0},
               {0},
               {0},
               0,
               0};
        raw< const Meta::Class > result = {&s_class};

        static Meta::ObjectInfo registry = {KernelScheduler::IProduct::getNamespace()->objects,
                                            {0},
                                            s_class.name,
                                            Meta::Value(result)};
        static const Meta::ObjectInfo* ptr
            = KernelScheduler::IProduct::getNamespace()->objects.set(&registry);
        motor_forceuse(ptr);

        return result;
    }
};

}  // namespace Meta
}  // namespace Motor

/**************************************************************************************************/
#endif
