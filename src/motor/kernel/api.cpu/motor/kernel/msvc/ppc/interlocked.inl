/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_KERNEL_MSVC_PPC_INTERLOCKED_INL
#define MOTOR_KERNEL_MSVC_PPC_INTERLOCKED_INL

#include <motor/kernel/stdafx.h>

extern "C"
{
    // NOLINTBEGIN(bugprone-reserved-identifier)
    long __cdecl _InterlockedCompareExchange(long volatile* dest, long exchange, long comp);
    long long __cdecl _InterlockedCompareExchange64(long long volatile* dest, long long exchange,
                                                    long long comp);
    long __cdecl _InterlockedExchange(long volatile* target, long value);
    long __cdecl _InterlockedExchangeAdd(long volatile* addend, long value);
    // NOLINTEND(bugprone-reserved-identifier)
}
#pragma intrinsic(_InterlockedExchange)
#pragma intrinsic(_InterlockedExchangeAdd)
#pragma intrinsic(_InterlockedCompareExchange)
#pragma intrinsic(_InterlockedCompareExchange64)

#pragma warning(push)
#pragma warning(disable : 4521)  // multiple copy constructor

namespace knl {

template < unsigned size >
struct InterlockedType;

template <>
struct InterlockedType< 4 >
{
    typedef __declspec(align(4)) long value_t;
    static inline value_t fetch(const volatile value_t* p)
    {
        return *p;
    }
    static inline value_t fetch_and_add(volatile value_t* p, value_t incr)
    {
        return _InterlockedExchangeAdd(p, incr);
    }
    static inline value_t fetch_and_sub(volatile value_t* p, value_t incr)
    {
        return _InterlockedExchangeAdd(p, -incr);
    }
    static inline value_t fetch_and_set(volatile value_t* p, value_t v)
    {
        return _InterlockedExchange(p, v);
    }
    static inline value_t set_conditional(volatile value_t* p, value_t v, value_t condition)
    {
        return _InterlockedCompareExchange(p, v, condition);
    }
    static inline value_t set_and_fetch(volatile value_t* p, value_t v)
    {
        _InterlockedExchange(p, v);
        return v;
    }

    struct tagged_t
    {
        typedef __declspec(align(4)) void* value_t;
        typedef __declspec(align(4)) long counter_t;
        typedef tagged_t tag_t;
        union
        {
            __declspec(align(8)) struct
            {
                volatile counter_t tag;
                volatile value_t   value;
            } tagged_value;
            __declspec(align(8)) volatile long long asLongLong;
        };
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
        explicit tagged_t(long long value) : asLongLong(value)
        {
        }
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
        explicit tagged_t(value_t value = nullptr) : tagged_value {0, value}
        {
        }
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-member-init)
        tagged_t(counter_t tag, value_t value) : tagged_value {tag, value}
        {
        }
        tagged_t(const tagged_t& other) = default;
        inline value_t value() const
        {
            return tagged_value.value;
        }
        tagged_t&   operator=(const tagged_t& other) = default;
        inline bool operator==(const tagged_t& other) const
        {
            return asLongLong == other.asLongLong;
        }
    };
    static inline tagged_t::tag_t get_ticket(const tagged_t& p)
    {
        return p;
    }
    static inline bool set_conditional(tagged_t* p, tagged_t::value_t v,
                                       const tagged_t::tag_t& condition)
    {
        tagged_t r(condition.tagged_value.tag + 1, v);
        return _InterlockedCompareExchange64(&(p->asLongLong), r.asLongLong, condition.asLongLong)
               == condition.asLongLong;
    }
};
template <>
struct InterlockedType< 1 > : public InterlockedType< 4 >
{
};
template <>
struct InterlockedType< 2 > : public InterlockedType< 4 >
{
};

}  // namespace knl

#pragma warning(pop)

#endif
