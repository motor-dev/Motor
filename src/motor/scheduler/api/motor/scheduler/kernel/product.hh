/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/producer.meta.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Product : public IProduct
{
public:
    Product(weak< const Producer > producer) : IProduct(producer)
    {
    }

    ~Product()
    {
    }

    ref< IParameter > createParameter() const override
    {
        return ref< T >::create(Arena::task());
    }
};

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/product.factory.hh>
