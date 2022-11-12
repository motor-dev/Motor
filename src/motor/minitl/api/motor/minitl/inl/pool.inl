/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

namespace minitl {

template < typename T >
pool< T >::pool(Allocator& allocator, u64 capacity, u64 alignment)
    : m_pool(allocator, capacity, alignment)
    , m_end(&m_pool[capacity])
{
    for(u64 i = 0; i < capacity; ++i)
        m_items.push(reinterpret_cast< node* >(&m_pool[i]));
}

template < typename T >
template < typename... Args >
T* pool< T >::allocate(Args&&... args)
{
    void* result = (void*)m_items.pop();
    motor_assert(result >= m_pool && result < m_end,
                 "allocated a node that is outside the node range");
    return new(result) T(forward< Args >(args)...);
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
