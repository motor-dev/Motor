/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PRODUCT_FACTORY_HH
#define MOTOR_SCHEDULER_KERNEL_PRODUCT_FACTORY_HH
#pragma once

#include <motor/scheduler/kernel/product.hh>

#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Product;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace Meta {

template < typename T >
struct ClassID< KernelScheduler::Product< T > >
{
    static Value construct(raw< const Meta::Method > method, Value* parameters, u32 parameterCount)
    {
        motor_forceuse(method);
        motor_assert_format(parameterCount == 1, "expected 1 parameter; got {0}", parameterCount);
        motor_forceuse(parameters);
        return Value(ref< KernelScheduler::Product< T > >::create(
            Arena::task(), parameters[0].as< weak< const KernelScheduler::Producer > >()));
    }

    static const Meta::Method::Overload s_ctrOverload;
    static const Meta::Method           s_ctr;

    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class = {name(),
                                            u32(sizeof(KernelScheduler::Product< T >)),
                                            motor_class< KernelScheduler::IProduct >(),
                                            0,
                                            motor_class< KernelScheduler::IProduct >()->objects,
                                            motor_class< KernelScheduler::IProduct >()->tags,
                                            motor_class< KernelScheduler::IProduct >()->properties,
                                            {&s_ctr},
                                            {&s_ctr},
                                            motor_class< KernelScheduler::IProduct >()->interfaces,
                                            nullptr,
                                            nullptr};
        raw< const Meta::Class > result  = {&s_class};

        static Meta::Object registry
            = {{KernelScheduler::IProduct::getNamespace()->objects.exchange(&registry)},
               s_class.name,
               Meta::Value(result)};
        motor_forceuse(registry);

        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("Product<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

template < typename T >
const Meta::Method::Overload ClassID< KernelScheduler::Product< T > >::s_ctrOverload
    = {{nullptr}, {nullptr, nullptr}, motor_type< ref< KernelScheduler::Product< T > > >(), false,
       false,     &construct};

template < typename T >
const Meta::Method ClassID< KernelScheduler::Product< T > >::s_ctr
    = {motor_class< KernelScheduler::IProduct >()->methods, istring("?ctor"), {&s_ctrOverload, 1}};

}}  // namespace Motor::Meta

#endif
