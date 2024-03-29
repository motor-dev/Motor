/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_SCOPEDPTR_HH
#define MOTOR_MINITL_SCOPEDPTR_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/utility.hh>

namespace minitl {

class allocator;

namespace details {

struct scoped_payload
{
    allocator& arena;

    MOTOR_ALWAYS_INLINE explicit scoped_payload(allocator& arena) : arena(arena)
    {
    }
    virtual ~scoped_payload()  // NOLINT(modernize-use-equals-default)
    {
    }
};

}  // namespace details

template < typename T >
class scoped
{
    template < typename U >
    friend class scoped;
    template < typename U, typename V >
    friend inline scoped< U > motor_checked_cast(scoped< V >&& value);

    struct payload : details::scoped_payload
    {
        struct value_wrapper
        {
            T value;
            template < typename... ARGS >
            MOTOR_ALWAYS_INLINE explicit value_wrapper(ARGS&&... args)
                : value(minitl::forward< ARGS >(args)...)
            {
            }
        };
        value_wrapper value;

        template < typename... ARGS >
        MOTOR_ALWAYS_INLINE explicit payload(allocator& arena, ARGS&&... args)
            : details::scoped_payload(arena)
            , value(minitl::forward< ARGS >(args)...)
        {
        }
    };

private:
    details::scoped_payload* m_payload;
    T*                       m_ptr;

private:
    MOTOR_ALWAYS_INLINE scoped(details::scoped_payload* payload, T* value);

public:
    MOTOR_ALWAYS_INLINE scoped& operator=(scoped&& other) noexcept;
    template < typename U >
    MOTOR_ALWAYS_INLINE scoped& operator=(scoped< U >&& other) noexcept;
    MOTOR_ALWAYS_INLINE         scoped();
    MOTOR_ALWAYS_INLINE ~scoped();
    MOTOR_ALWAYS_INLINE scoped(scoped&& other) noexcept;
    template < typename U >
    MOTOR_ALWAYS_INLINE scoped(scoped< U >&& other);  // NOLINT(google-explicit-constructor)

public:
    scoped(const scoped& other) = delete;
    template < typename U >
    scoped(const scoped< U >& other) = delete;
    template < typename U >
    scoped& operator=(const scoped< U >& other) = delete;
    scoped& operator=(const scoped& other)      = delete;

    MOTOR_ALWAYS_INLINE T* operator->() const;
    MOTOR_ALWAYS_INLINE operator const void*() const;  // NOLINT(google-explicit-constructor)
    MOTOR_ALWAYS_INLINE bool operator!() const;
    MOTOR_ALWAYS_INLINE T&   operator*();

    template < typename... ARGS >
    static MOTOR_ALWAYS_INLINE scoped< T > create(allocator& allocator, ARGS&&... args);
};

}  // namespace minitl

#include <motor/minitl/inl/scopedptr.hh>

#endif
