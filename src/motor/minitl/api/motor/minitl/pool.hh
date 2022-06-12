/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_POOL_
#define MOTOR_MINITL_POOL_
/**************************************************************************************************/
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
    struct node : public minitl::istack< node >::node
    {
    };
    enum
    {
        ElementSize = sizeof(T)
    };
    istack< node >        m_items;
    Allocator::Block< T > m_pool;
    T*                    m_end;

public:
    pool(Allocator& allocator, u64 capacity, u64 alignment = motor_alignof(T));
    pool(pool&& other)            = default;
    pool& operator=(pool&& other) = default;
    ~pool()                       = default;

    pool(const pool& other)            = delete;
    pool& operator=(const pool& other) = delete;

    template < typename... Args >
    T*   allocate(Args&&... args);
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

/**************************************************************************************************/
#endif
