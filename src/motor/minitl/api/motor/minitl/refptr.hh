/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_REFPTR_HH
#define MOTOR_MINITL_REFPTR_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/pointer.hh>
#include <motor/minitl/utility.hh>

namespace minitl {

class allocator;

namespace details {

struct ref_payload
{
    allocator& arena;
    i_u32      reference_count;

    MOTOR_ALWAYS_INLINE explicit ref_payload(allocator& arena) : arena(arena), reference_count({})
    {
    }
    virtual ~ref_payload() = default;
};

}  // namespace details

template < typename T >
class ref
{
    template < typename U, typename V >
    friend ref< U > motor_checked_cast(const ref< V >& v);
    template < typename U >
    friend class ref;

    struct payload : details::ref_payload
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
            : details::ref_payload(arena)
            , value(minitl::forward< ARGS >(args)...)
        {
        }
        MOTOR_ALWAYS_INLINE ~payload() override = default;
    };

private:
    details::ref_payload* m_payload;
    T*                    m_ptr;

private:
    MOTOR_ALWAYS_INLINE void swap(ref& other);

private:
    MOTOR_ALWAYS_INLINE ref(details::ref_payload* payload, T* value);

public:
    MOTOR_ALWAYS_INLINE ref();
    MOTOR_ALWAYS_INLINE ref(const ref& other);
    template < typename U >
    MOTOR_ALWAYS_INLINE ref(const ref< U >& other);  // NOLINT(google-explicit-constructor)
    MOTOR_ALWAYS_INLINE ref(ref&& other) noexcept;
    template < typename U >
    explicit MOTOR_ALWAYS_INLINE ref(ref< U >&& other) noexcept;

    MOTOR_ALWAYS_INLINE ref& operator=(const ref& other);
    template < typename U >
    MOTOR_ALWAYS_INLINE ref& operator=(const ref< U >& other);
    MOTOR_ALWAYS_INLINE ref& operator=(ref&& other) noexcept;
    template < typename U >
    MOTOR_ALWAYS_INLINE ref& operator=(ref< U >&& other) noexcept;

    MOTOR_ALWAYS_INLINE ~ref();

    MOTOR_ALWAYS_INLINE T* operator->() const;
    MOTOR_ALWAYS_INLINE operator const void*() const;  // NOLINT(google-explicit-constructor)
    MOTOR_ALWAYS_INLINE bool operator!() const;
    MOTOR_ALWAYS_INLINE T&   operator*();

    inline void clear();
    template < typename... ARGS >
    static MOTOR_ALWAYS_INLINE ref< T > create(allocator& allocator, ARGS&&... args)
    {
        auto* p = new(allocator.alloc(sizeof(payload)))
            payload(allocator, minitl::forward< ARGS >(args)...);
        return ref< T >(p, reinterpret_cast< T* >(&p->value));
    }
};

}  // namespace minitl

#include <motor/minitl/inl/refptr.hh>

#endif
