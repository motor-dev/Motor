/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/kernel/stdafx.h>
#include <sanitizer/tsan_interface_atomic.h>

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
        } taggedvalue;

        inline tagged_t(value_t value = 0);
        inline tagged_t(counter_t tag, value_t value);
        inline tagged_t(const tagged_t& other);
        inline tagged_t& operator=(const tagged_t& other);
        inline value_t   value();
        inline bool      operator==(tagged_t& other);
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
        } taggedvalue;

        inline tagged_t(value_t value = 0);
        inline tagged_t(counter_t tag, value_t value);
        inline tagged_t(const tagged_t& other);
        inline tagged_t& operator=(const tagged_t& other);
        inline value_t   value();
        inline bool      operator==(tagged_t& other);
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
    return __tsan_atomic32_load(p, __tsan_memory_order_acquire);
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::fetch_and_add(value_t* p, value_t incr)
{
    return __tsan_atomic32_fetch_add(p, incr, __tsan_memory_order_acq_rel);
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::fetch_and_sub(value_t* p, value_t incr)
{
    return __tsan_atomic32_fetch_add(p, -incr, __tsan_memory_order_acq_rel);
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::fetch_and_set(value_t* p, value_t v)
{
    return __tsan_atomic32_exchange(p, v, __tsan_memory_order_acq_rel);
}

InterlockedType< 4 >::value_t InterlockedType< 4 >::set_conditional(value_t* p, value_t v,
                                                                    value_t condition)
{
    return __tsan_atomic32_compare_exchange_val(p, condition, v, __tsan_memory_order_acq_rel,
                                                __tsan_memory_order_relaxed);
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
    tagged_t::tag_t value(condition.taggedvalue.tag + 1, v);
    return __tsan_atomic64_compare_exchange_strong(
        (__tsan_atomic64*)p, (__tsan_atomic64*)&condition, *(__tsan_atomic64*)&value,
        __tsan_memory_order_acq_rel, __tsan_memory_order_relaxed);
}

InterlockedType< 4 >::tagged_t::tagged_t(value_t value)
{
    taggedvalue.tag   = 0;
    taggedvalue.value = value;
}

InterlockedType< 4 >::tagged_t::tagged_t(counter_t tag, value_t value)
{
    taggedvalue.tag   = tag;
    taggedvalue.value = value;
}

InterlockedType< 4 >::tagged_t::tagged_t(const tagged_t& other)
{
    taggedvalue.tag   = other.taggedvalue.tag;
    taggedvalue.value = other.taggedvalue.value;
}

InterlockedType< 4 >::tagged_t& InterlockedType< 4 >::tagged_t::operator=(const tagged_t& other)
{
    taggedvalue.tag   = other.taggedvalue.tag;
    taggedvalue.value = other.taggedvalue.value;
    return *this;
}

InterlockedType< 4 >::tagged_t::value_t InterlockedType< 4 >::tagged_t::value()
{
    return taggedvalue.value;
}

bool InterlockedType< 4 >::tagged_t::operator==(tagged_t& other)
{
    return (taggedvalue.tag == other.taggedvalue.tag)
           && (taggedvalue.value == other.taggedvalue.value);
}

InterlockedType< 8 >::tagged_t::tagged_t(value_t value)
{
    taggedvalue.tag   = 0;
    taggedvalue.value = value;
}

InterlockedType< 8 >::tagged_t::tagged_t(counter_t tag, value_t value)
{
    taggedvalue.tag   = tag;
    taggedvalue.value = value;
}

InterlockedType< 8 >::tagged_t::tagged_t(const tagged_t& other)
{
    taggedvalue.tag   = other.taggedvalue.tag;
    taggedvalue.value = other.taggedvalue.value;
}

InterlockedType< 8 >::tagged_t& InterlockedType< 8 >::tagged_t::operator=(const tagged_t& other)
{
    taggedvalue.tag   = other.taggedvalue.tag;
    taggedvalue.value = other.taggedvalue.value;
    return *this;
}

InterlockedType< 8 >::tagged_t::value_t InterlockedType< 8 >::tagged_t::value()
{
    return (value_t)__tsan_atomic64_load((__tsan_atomic64*)&taggedvalue.value,
                                         __tsan_memory_order_acquire);
}

bool InterlockedType< 8 >::tagged_t::operator==(tagged_t& other)
{
    return (taggedvalue.tag == other.taggedvalue.tag)
           && (taggedvalue.value == other.taggedvalue.value);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch(const value_t* p)
{
    return __tsan_atomic64_load(p, __tsan_memory_order_acquire);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch_and_add(value_t* p, value_t incr)
{
    return __tsan_atomic64_fetch_add(p, incr, __tsan_memory_order_acq_rel);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch_and_sub(value_t* p, value_t incr)
{
    return fetch_and_add(p, -incr);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::fetch_and_set(value_t* p, value_t v)
{
    return __tsan_atomic64_exchange(p, v, __tsan_memory_order_acq_rel);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::set_conditional(value_t* p, value_t v,
                                                                    value_t condition)
{
    return __tsan_atomic64_compare_exchange_val((__tsan_atomic64*)p, condition, v,
                                                __tsan_memory_order_acq_rel,
                                                __tsan_memory_order_relaxed);
}

InterlockedType< 8 >::value_t InterlockedType< 8 >::set_and_fetch(value_t* p, value_t v)
{
    fetch_and_set(p, v);
    return v;
}

InterlockedType< 8 >::tagged_t::tag_t InterlockedType< 8 >::get_ticket(const tagged_t& p)
{
    tagged_t::tag_t result;
    *(__tsan_atomic128*)&result
        = __tsan_atomic128_load((__tsan_atomic128*)&p, __tsan_memory_order_acquire);
    return result;
}

bool InterlockedType< 8 >::set_conditional(tagged_t* p, tagged_t::value_t v,
                                           const tagged_t::tag_t& condition)
{
    tagged_t::tag_t value(condition.taggedvalue.tag + 1, v);
    return __tsan_atomic128_compare_exchange_strong(
        (__tsan_atomic128*)p, (__tsan_atomic128*)&condition, *(__tsan_atomic128*)&value,
        __tsan_memory_order_acq_rel, __tsan_memory_order_relaxed);
}

}  // namespace knl
