/* Motor <motor.devel@gmail.com>
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

}  // namespace minitl

#include <motor/minitl/inl/pool.inl>
