/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>

namespace Motor { namespace Meta {

template < typename T >
struct staticarray
{
    u32 const count;
    T* const  elements;

    inline T&       operator[](u32 index);
    inline const T& operator[](u32 index) const;

    inline T*       begin();
    inline const T* begin() const;
    inline T*       end();
    inline const T* end() const;
};

template < typename T >
T& staticarray< T >::operator[](const u32 index)
{
    motor_assert_format(index < count, "index {0} out of range (0, {1})", index, (count - 1));
    return *(begin() + index);
}

template < typename T >
const T& staticarray< T >::operator[](const u32 index) const
{
    motor_assert_format(index < count, "index {0} out of range (0, {1})", index, (count - 1));
    return *(begin() + index);
}

template < typename T >
T* staticarray< T >::begin()
{
    return elements;
}

template < typename T >
const T* staticarray< T >::begin() const
{
    return elements;
}

template < typename T >
T* staticarray< T >::end()
{
    return begin() + count;
}

template < typename T >
const T* staticarray< T >::end() const
{
    return begin() + count;
}

}}  // namespace Motor::Meta
