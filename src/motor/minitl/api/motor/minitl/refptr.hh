/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_REFPTR_HH
#define MOTOR_MINITL_REFPTR_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/refcountable.hh>
#include <motor/minitl/utility.hh>

namespace minitl {

template < typename T >
class ref
{
    template < typename U, typename V >
    friend ref< U > motor_checked_cast(ref< V > v);
    friend class refcountable;
    template < typename U >
    friend class ref;

private:
    T* m_ptr;

private:
    inline void swap(ref& other);

private:
    inline explicit ref(T* value);
    inline ref(T* value, allocator& deleter);

public:
    inline ref();
    inline ref(const ref& other);
    template < typename U >
    inline ref(const ref< U >& other);  // NOLINT(google-explicit-constructor)
    template < typename U >
    inline explicit ref(scoped< U >&& other) noexcept;
    inline ref(ref&& other) noexcept;
    template < typename U >
    explicit inline ref(ref< U >&& other) noexcept;

    inline ref& operator=(const ref& other);
    template < typename U >
    inline ref& operator=(const ref< U >& other);
    inline ref& operator=(ref&& other) noexcept;
    template < typename U >
    inline ref& operator=(ref< U >&& other) noexcept;

    inline ~ref();

    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool            operator!() const;
    MOTOR_ALWAYS_INLINE T& operator*();

    inline void clear();
    template < typename... ARGS >
    static inline ref< T > create(allocator& allocator, ARGS&&... args)
    {
        void* mem = allocator.alloc(sizeof(T), motor_alignof(T));
        return ref< T >(new(mem) T(minitl::forward< ARGS >(args)...), allocator);
    }
};

}  // namespace minitl

#include <motor/minitl/inl/refptr.hh>

#endif
