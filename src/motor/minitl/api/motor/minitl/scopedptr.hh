/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_SCOPEDPTR_HH_
#define MOTOR_MINITL_SCOPEDPTR_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/utility.hh>

namespace minitl {

template < typename T >
class scoped
{
    template < typename U >
    friend class scoped;
    template < typename U >
    friend class ref;

private:
    T* m_ptr;

private:
    scoped(T* value, Allocator& deleter);
    scoped(const scoped& other) = delete;
    template < typename U >
    inline scoped(const scoped< U >& other) = delete;
    template < typename U >
    scoped& operator=(const scoped< U >& other) = delete;
    scoped& operator=(const scoped& other)      = delete;

public:
    inline scoped();
    inline ~scoped();
    inline scoped(scoped&& other);
    template < typename U >
    inline scoped(scoped< U >&& other);

    inline T*   operator->() const;
    inline      operator const void*() const;
    inline bool operator!() const;
    inline T&   operator*();

    template < typename U >
    inline void reset(scoped< U >&& other);

    template < typename... Args >
    static inline scoped< T > create(Allocator& allocator, Args&&... args)
    {
        void* mem = allocator.alloc(sizeof(T), motor_alignof(T));
        return scoped< T >(new(mem) T(minitl::forward< Args >(args)...), allocator);
    }
};

template < u16 SIZE >
class format;
template < typename T, u16 SIZE >
const format< SIZE >& operator|(const format< SIZE >& format, const scoped< T >& t)
{
    return format | t.operator->();
}

}  // namespace minitl

#include <motor/minitl/inl/scopedptr.inl>

/**************************************************************************************************/
#endif
