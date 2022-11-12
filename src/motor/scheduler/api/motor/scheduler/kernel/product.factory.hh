/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/iproduct.meta.hh>

#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
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
        motor_assert(parameterCount == 1, "expected 1 parameter; got %d" | parameterCount);
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
                                            0,
                                            Meta::ClassType_Object,
                                            {KernelScheduler::IProduct::getNamespace().m_ptr},
                                            {motor_class< KernelScheduler::IProduct >().m_ptr},
                                            {0},
                                            {0},
                                            {0, 0},
                                            {1, &s_ctr},
                                            {&s_ctr},
                                            Meta::OperatorTable::s_emptyTable,
                                            0,
                                            0};
        raw< const Meta::Class > result  = {&s_class};

        static Meta::ObjectInfo registry = {KernelScheduler::IProduct::getNamespace()->objects,
                                            {0},
                                            s_class.name,
                                            Meta::Value(result)};
        static const Meta::ObjectInfo* ptr
            = KernelScheduler::IProduct::getNamespace()->objects.set(&registry);
        motor_forceuse(ptr);

        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(minitl::format< 2048u >("Product<%s>") | TypeID< T >::name());
        return s_name;
    }
};

template < typename T >
const Meta::Method::Overload ClassID< KernelScheduler::Product< T > >::s_ctrOverload
    = {{0}, {0, 0}, motor_type< ref< KernelScheduler::Product< T > > >(), false, &construct};

template < typename T >
const Meta::Method ClassID< KernelScheduler::Product< T > >::s_ctr
    = {Meta::Class::nameConstructor(),
       {1, &s_ctrOverload},
       {&ClassID< KernelScheduler::Product< T > >::s_ctr}};

}}  // namespace Motor::Meta
