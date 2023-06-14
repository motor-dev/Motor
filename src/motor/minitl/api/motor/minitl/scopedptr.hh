/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_SCOPEDPTR_HH
#define MOTOR_MINITL_SCOPEDPTR_HH

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
    scoped(T* value, allocator& allocator);

public:
    scoped(const scoped& other) = delete;
    template < typename U >
    inline scoped(const scoped< U >& other) = delete;
    template < typename U >
    scoped& operator=(const scoped< U >& other) = delete;
    scoped& operator=(const scoped& other)      = delete;
    inline scoped();
    inline ~scoped();
    inline scoped(scoped&& other) noexcept;
    template < typename U >
    inline scoped(scoped< U >&& other);  // NOLINT(google-explicit-constructor)

    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool            operator!() const;
    MOTOR_ALWAYS_INLINE T& operator*();

    template < typename U >
    inline void reset(scoped< U >&& other);

    template < typename... ARGS >
    static inline scoped< T > create(allocator& allocator, ARGS&&... args)
    {
        void* mem = allocator.alloc(sizeof(T), motor_alignof(T));
        return scoped< T >(new(mem) T(minitl::forward< ARGS >(args)...), allocator);
    }
};

}  // namespace minitl

#include <motor/minitl/inl/scopedptr.hh>

#endif
