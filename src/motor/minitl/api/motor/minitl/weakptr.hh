/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_WEAKPTR_HH
#define MOTOR_MINITL_WEAKPTR_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/pointer.hh>

namespace minitl {

template < typename T >
class weak
{
    template < typename U >
    friend class weak;
    template < typename U, typename V >
    friend weak< U > motor_checked_cast(const weak< V >& v);

private:
    T* m_ptr;

private:
    inline void swap(weak& other);

public:
    inline weak();
    inline weak(T* p);                      // NOLINT(google-explicit-constructor)
    template < typename U >
    inline weak(const ref< U >& other);     // NOLINT(google-explicit-constructor)
    template < typename U >
    inline weak(const scoped< U >& other);  // NOLINT(google-explicit-constructor)
    inline weak(const weak& other);
    inline weak(weak&& other) noexcept;
    template < typename U >
    inline weak(const weak< U >& other);      // NOLINT(google-explicit-constructor)
    template < typename U >
    inline weak(weak< U >&& other) noexcept;  // NOLINT(google-explicit-constructor)
    inline ~weak();

    inline weak& operator=(const weak& other);
    template < typename U >
    inline weak& operator=(const weak< U >& other);
    inline weak& operator=(weak&& other) noexcept;
    template < typename U >
    inline weak& operator=(weak< U >&& other) noexcept;
    template < typename U >
    inline weak& operator=(U* other);

    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool            operator!() const;
    MOTOR_ALWAYS_INLINE T& operator*();

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

}  // namespace minitl

#include <motor/minitl/inl/weakptr.hh>

#endif
