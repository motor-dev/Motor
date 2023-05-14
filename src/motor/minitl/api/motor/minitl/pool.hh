/*  */ /* Motor <motor.devel@gmail.com>
    see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/kernel/interlocked.hh>
#include <motor/kernel/interlocked_stack.hh>
#include <motor/minitl/allocator.hh>
#include <motor/minitl/swap.hh>

namespace minitl {

template < typename T >
class pool
{
private:
    struct node : public knl::istack< node >::node
    {
    };
    knl::istack< node >   m_items;
    allocator::block< T > m_pool;
    T*                    m_end;

public:
    pool(allocator& allocator, u64 capacity, u64 alignment = motor_alignof(T));
    pool(pool&& other)            = default;  // NOLINT(performance-noexcept-move-constructor)
    pool& operator=(pool&& other) = default;  // NOLINT(performance-noexcept-move-constructor)
    ~pool()                       = default;

    pool(const pool& other)            = delete;
    pool& operator=(const pool& other) = delete;

    template < typename... ARGS >
    T*   allocate(ARGS&&... args);
    void release(T* t);

    void swap(pool< T >& other);
};

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
    void* result = (void*)m_items.pop();
    motor_assert(result >= m_pool && result < m_end,
                 "allocated a node that is outside the node range");
    return new(result) T(forward< ARGS >(args)...);
}

template < typename T >
void pool< T >::release(T* t)
{
    t->~T();
    motor_assert(t >= m_pool && t < m_end, "releasing a node that is outside the node range");
    m_items.push((node*)t);
}

template < typename T >
void pool< T >::swap(pool< T >& other)
{
    minitl::swap(m_items, other.m_items);
    m_pool.swap(other.m_pool);
    minitl::swap(m_end, other.m_end);
}

}  // namespace minitl
