/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_WEAKPTR_HH_
#define MOTOR_MINITL_WEAKPTR_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/minitl/refptr.hh>
#include <motor/minitl/scopedptr.hh>

namespace minitl {

template < typename T >
class weak
{
    template < typename U, typename V >
    friend weak< U > motor_checked_cast(weak< V > v);
    template < typename U, typename V >
    friend weak< U > motor_const_cast(weak< V > v);

private:
    T* m_ptr;

private:
    inline void swap(weak& other);

public:
    inline weak();
    inline weak(T* p);
    template < typename U >
    inline weak(ref< U > other);
    template < typename U >
    inline weak(const scoped< U >& other);
    inline weak(const weak& other);
    template < typename U >
    inline weak(const weak< U >& other);
    inline ~weak();

    inline weak& operator=(const weak& other);
    template < typename U >
    inline weak& operator=(const weak< U >& other);
    template < typename U >
    inline weak& operator=(U* other);

    inline T*   operator->() const;
    inline      operator const void*() const;
    inline bool operator!() const;
    inline T&   operator*();

    inline void clear();
};

template < typename T >
struct hash< weak< T > >
{
    u32 operator()(weak< T > t)
    {
        return hash< T* >()(t.operator->());
    }
    bool operator()(weak< T > t1, weak< T > t2)
    {
        return hash< T* >()(t1.operator->(), t2.operator->());
    }
};

template < u16 SIZE >
class format;
template < typename T, u16 SIZE >
const format< SIZE >& operator|(const format< SIZE >& format, weak< T > t)
{
    return format | t.operator->();
}

}  // namespace minitl

#include <motor/minitl/inl/weakptr.inl>

/**************************************************************************************************/
#endif
