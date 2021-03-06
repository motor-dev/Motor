/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_ARRAY_HH_
#define MOTOR_MINITL_ARRAY_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/kernel/interlocked.hh>
#include <motor/minitl/algorithm.hh>
#include <motor/minitl/allocator.hh>
#include <motor/minitl/swap.hh>

namespace minitl {

template < typename T >
class array
{
private:
    minitl::Allocator::Block< T > m_array;

private:
    array& operator=(const array& other);

public:
    typedef const T* const_iterator;
    typedef T*       iterator;

public:
    inline array(Allocator& allocator, u32 size);
    template < typename ITERATOR >
    inline array(Allocator& allocator, ITERATOR begin, ITERATOR end);
    inline array(const array& other);
    inline array(array&& other);
    inline ~array();

    inline void swap(array& other);

    inline iterator       begin();
    inline iterator       end();
    inline const_iterator begin() const;
    inline const_iterator end() const;

    inline T&       operator[](u32 index);
    inline const T& operator[](u32 index) const;

    inline u32 size() const;

    T&       first();
    const T& first() const;
    T&       last();
    const T& last() const;
};

template < typename T >
void swap(array< T >& a, array< T >& b)
{
    a.swap(b);
}

}  // namespace minitl

#include <motor/minitl/inl/array.inl>

/**************************************************************************************************/
#endif
