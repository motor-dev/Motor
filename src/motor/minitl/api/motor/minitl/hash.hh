/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_HASH_HH_
#define MOTOR_MINITL_HASH_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <cstring>

namespace minitl {

template < typename T >
struct hash;

template < typename T >
struct hash< const T* > : public hash< T* >
{
};

template < typename T >
struct hash< T* >
{
    u32 operator()(const T* t) const
    {
        return u32(intptr_t(t));
    }
    bool operator()(const T* t1, const T* t2) const
    {
        return t1 == t2;
    }
};

}  // namespace minitl

/**************************************************************************************************/
#endif
