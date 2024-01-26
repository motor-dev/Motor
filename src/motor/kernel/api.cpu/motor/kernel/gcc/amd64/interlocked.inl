/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_KERNEL_GCC_X86_INTERLOCKED_INL
#    define MOTOR_KERNEL_GCC_X86_INTERLOCKED_INL

#    include <motor/kernel/stdafx.h>

// NOLINTBEGIN(readability-non-const-parameter)

namespace knl {

template < unsigned size >
struct InterlockedType;

template <>
struct InterlockedType< 4 >
{
    typedef __attribute__((aligned(4))) i32 value_t;

    struct tagged_t
    {
        typedef __attribute__((aligned(4))) void* value_t;
        typedef __attribute__((aligned(4))) i32   counter_t;
        typedef tagged_t                          tag_t;
        __attribute__((aligned(8))) struct
        {
            counter_t        tag;
            volatile value_t value;
        } tagged_value;

        inline explicit tagged_t(value_t value = nullptr);
        inline tagged_t(const tagged_t& other)            = default;
        inline tagged_t& operator=(const tagged_t& other) = default;
        inline value_t   value() const;
        inline bool      operator==(tagged_t& other) const;
    };

    static inline value_t fetch(const value_t* p);
    static inline value_t fetch_and_add(value_t* p, value_t incr);
    static inline value_t fetch_and_sub(value_t* p, value_t incr);

    static inline value_t set_conditional(value_t* p, value_t v, value_t condition);
    static inline value_t set_and_fetch(value_t* p, value_t v);
    static inline value_t fetch_and_set(value_t* p, value_t v);

    static inline tagged_t::tag_t get_ticket(const tagged_t& p);
    static inline bool            set_conditional(tagged_t* p, tagged_t::value_t v,
                                                  const tagged_t::tag_t& condition);
};

template <>
struct InterlockedType< 1 > : public InterlockedType< 4 >
{
};

template <>
struct InterlockedType< 2 > : public InterlockedType< 4 >
{
};

template <>
struct InterlockedType< 8 >
{
    typedef __attribute__((aligned(8))) i64 value_t;

    struct tagged_t
    {
        typedef __attribute__((aligned(8))) void* value_t;
        typedef __attribute__((aligned(8))) i64   counter_t;
        typedef tagged_t                          tag_t;
        __attribute__((aligned(16))) struct
        {
            counter_t tag;
            value_t   value;
        } tagged_value;

        inline explicit tagged_t(value_t value = nullptr);
        inline tagged_t(const tagged_t& other)            = default;
        inline tagged_t& operator=(const tagged_t& other) = default;
        inline value_t   value() const;
        inline bool      operator==(tagged_t& other) const;
    };

    static inline value_t fetch(const value_t* p);
    static inline value_t fetch_and_add(value_t* p, value_t incr);
    static inline value_t fetch_and_sub(value_t* p, value_t incr);

    static inline value_t fetch_and_set(value_t* p, value_t v);
    static inline value_t set_conditional(value_t* p, value_t v, value_t condition);
    static inline value_t set_and_fetch(value_t* p, value_t v);

    static inline tagged_t::tag_t get_ticket(const tagged_t& p);
    static inline bool            set_conditional(tagged_t* p, tagged_t::value_t v,
                                                  const tagged_t::tag_t& condition);
};

InterlockedType< 4 >::value_t InterlockedType< 4 >::fetch(const value_t* p)
{
    return *p;
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::fetch_and_add(value_t* p, value_t incr)
{
    value_t old;
    __asm__ __volatile__("lock; xadd %0,%1" : "=r"(old), "+m"(*p) : "0"(incr) : "memory");
    return old;
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::fetch_and_sub(value_t* p, value_t incr)
{
    return fetch_and_add(p, -incr);
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::fetch_and_set(value_t* p, value_t v)
{
    __asm__ __volatile__("lock; xchg %0, %1" : "+r"(v), "+m"(*p) : : "memory");
    return v;
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::set_conditional(value_t* p, value_t v,
                                                                    value_t condition)
{
    value_t old;
    __asm__ __volatile__("lock; cmpxchg %2, %1"
                         : "=a"(old), "+m"(*p)
                         : "r"(v), "a"(condition)
                         : "memory", "cc");
    return old;
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::set_and_fetch(value_t* p, value_t v)
{
    fetch_and_set(p, v);
    return v;
}

InterlockedType< 4 >::tagged_t::tag_t InterlockedType< 4 >::get_ticket(const tagged_t& p)
{
    return p;
}

bool InterlockedType< 4 >::set_conditional(tagged_t* p, tagged_t::value_t v,
                                           const tagged_t::tag_t& condition)
{
    unsigned char     result;
    tagged_t::value_t unused;
    __asm__ __volatile__("       push %%ebx\n\t"
                         "       mov %%eax,%%ebx\n\t"
                         "       inc %%ebx\n\t"
                         "lock;  cmpxchg8b (%3)\n\t"
                         "       setz %1\n\t"
                         "       pop %%ebx\n\t"
                         : "=m"(*p), "=a"(result), "=d"(unused)
                         : "S"(p), "a"(condition.tagged_value.tag),
                           "d"(condition.tagged_value.value), "c"(v)
                         : "memory", "cc");
    motor_forceuse(unused);
    return result;
}

InterlockedType< 4 >::tagged_t::tagged_t(value_t value) : tagged_value {0, value}
{
}

InterlockedType< 4 >::tagged_t::value_t InterlockedType< 4 >::tagged_t::value() const
{
    return tagged_value.value;
}

bool InterlockedType< 4 >::tagged_t::operator==(tagged_t& other) const
{
    return (tagged_value.tag == other.tagged_value.tag)
           && (tagged_value.value == other.tagged_value.value);
}

InterlockedType< 8 >::tagged_t::tagged_t(value_t value) : tagged_value {0, value}
{
}

InterlockedType< 8 >::tagged_t::value_t InterlockedType< 8 >::tagged_t::value() const
{
    return tagged_value.value;
}

bool InterlockedType< 8 >::tagged_t::operator==(tagged_t& other) const
{
    return (tagged_value.tag == other.tagged_value.tag)
           && (tagged_value.value == other.tagged_value.value);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch(const value_t* p)
{
    return *p;
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch_and_add(value_t* p, value_t incr)
{
    value_t old;
    __asm__ __volatile__("lock; xaddq %0,%1" : "=r"(old), "=m"(*p) : "0"(incr), "m"(*p) : "memory");
    return old;
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch_and_sub(value_t* p, value_t incr)
{
    return fetch_and_add(p, -incr);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch_and_set(value_t* p, value_t v)
{
    __asm__ __volatile__("lock; xchgq %2, %1" : "=r"(v), "+m"(*p) : "0"(v) : "memory");
    return v;
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::set_conditional(value_t* p, value_t v,
                                                                    value_t condition)
{
    union split
    {
        i64 asI64 {};
        i32 asI32[2];
    };
    split dst {v};
    split src {condition};
    split result {0};

    __asm__ __volatile__("lock;  cmpxchg8b %2\n\t"
                         : "=a"(result.asI32[0]), "=d"(result.asI32[1]), "=m"(*p)
                         : "m"(*p), "a"(src.asI32[0]), "d"(src.asI32[1]), "b"(dst.asI32[0]),
                           "c"(dst.asI32[1])
                         : "memory", "cc"

    );
    return result.asI64;
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::set_and_fetch(value_t* p, value_t v)
{
    fetch_and_set(p, v);
    return v;
}

InterlockedType< 8 >::tagged_t::tag_t InterlockedType< 8 >::get_ticket(const tagged_t& p)
{
    return p;
}

bool InterlockedType< 8 >::set_conditional(tagged_t* p, tagged_t::value_t v,
                                           const tagged_t::tag_t& condition)
{
    unsigned char   result;
    tagged_t::tag_t dummy;
    __asm__ __volatile__("\tmov %4,%%r8\n"
                         "\t.byte 0xF0,0x49,0x0F,0xC7,0x08\n"
                         "\tsetz %0\n"
                         : "=r"(result), "=m"(*p), "=d"(dummy.tagged_value.value),
                           "=a"(dummy.tagged_value.tag)
                         : "r"(p), "c"(v), "b"(condition.tagged_value.tag + 1),
                           "d"(condition.tagged_value.value), "a"(condition.tagged_value.tag)
                         : "memory", "cc", "r8");
    return result;
}

#endif

}  // namespace knl

// NOLINTEND(readability-non-const-parameter)
