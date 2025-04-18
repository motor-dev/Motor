/*  */ /* Motor <motor.devel@gmail.com>
    see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_POOL_HH
#define MOTOR_MINITL_INL_POOL_HH
#pragma once

#include <motor/minitl/pool.hh>

namespace minitl {

template < typename T >
void swap(pool< T >& a, pool< T >& b)
{
    a.swap(b);
}

template < typename T >
pool< T >::pool(allocator& allocator, u64 capacity, u64 alignment)
    : m_pool(allocator, capacity, alignment)
    , m_end(&m_pool[capacity])
{
    for(u64 i = 0; i < capacity; ++i)
        m_items.push(reinterpret_cast< node* >(&m_pool[i]));
}

template < typename T >
template < typename... ARGS >
T* pool< T >::allocate(ARGS&&... args)
{
    auto result = static_cast< void* >(m_items.pop());
    motor_assert(result >= m_pool && result < m_end,
                 "allocated a node that is outside the node range");
    return new(result) T(minitl::forward< ARGS >(args)...);
}

template < typename T >
void pool< T >::release(T* t)
{
    t->~T();
    motor_assert(t >= m_pool && t < m_end, "releasing a node that is outside the node range");
    m_items.push(reinterpret_cast< node* >(t));
}

template < typename T >
void pool< T >::swap(pool< T >& other)
{
    minitl::swap(m_items, other.m_items);
    m_pool.swap(other.m_pool);
    minitl::swap(m_end, other.m_end);
}

}  // namespace minitl

#endif
