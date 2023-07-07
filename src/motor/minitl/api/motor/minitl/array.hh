/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_ARRAY_HH
#define MOTOR_MINITL_ARRAY_HH

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T, u32 COUNT >
class array
{
private:
    T m_array[COUNT];

public:
    typedef const T* const_iterator;
    typedef T*       iterator;

public:
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

}  // namespace minitl

#include <motor/minitl/inl/array.hh>

#endif