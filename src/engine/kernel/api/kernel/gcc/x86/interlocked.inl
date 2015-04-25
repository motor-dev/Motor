/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_KERNEL_GCC_X86_INTERLOCKED_INL_
#define BE_KERNEL_GCC_X86_INTERLOCKED_INL_
/**************************************************************************************************/
#include    <kernel/stdafx.h>

namespace _Kernel
{

template< unsigned size >
struct InterlockedType;


template<>
struct InterlockedType<4>
{
    typedef __attribute__ ((aligned(4))) i32 value_t;
    static inline value_t fetch_and_add(value_t *p, value_t incr)
    {
        value_t old;
        __asm__ __volatile__ ("lock; xadd %0,%1"
                      : "=r" (old), "+m" (*p)
                      : "0" (incr)
                      : "memory");
        return old;
    }
    static inline value_t fetch_and_sub(value_t *p, value_t incr)
    {
        return fetch_and_add(p, -incr);
    }
    static inline value_t fetch_and_set(value_t *p, value_t v)
    {
        __asm__ __volatile__ ("lock; xchg %0, %1"
                      : "+r" (v), "+m" (*p)
                      :
                      : "memory");
        return v;
    }

    static inline value_t set_conditional(value_t *p, value_t v, value_t condition)
    {
        value_t old;
        __asm__ __volatile__ ("lock; cmpxchg %2, %1"
                      : "=a" (old), "+m" (*p)
                      : "r"(v), "a"(condition)
                      : "memory", "cc");
        return old;
    }
    static inline value_t set_and_fetch(value_t *p, value_t v)
    {
        fetch_and_set(p, v);
        return v;
    }

    struct tagged_t
    {
        typedef __attribute__ ((aligned(4))) void*  value_t;
        typedef __attribute__ ((aligned(4))) i32    counter_t;
        typedef tagged_t    tag_t;
        __attribute__ ((aligned(8))) struct
        {
            counter_t           tag;
            volatile value_t     value;
        } taggedvalue;

        tagged_t(value_t value = 0)
        {
            taggedvalue.tag = 0;
            taggedvalue.value = value;
        }
        tagged_t(counter_t tag, value_t value)
        {
            taggedvalue.tag = tag;
            taggedvalue.value = value;
        }
        tagged_t(const tagged_t& other)
        {
            taggedvalue.tag = other.taggedvalue.tag;
            taggedvalue.value = other.taggedvalue.value;
        }
        tagged_t& operator=(const tagged_t& other)
        {
            taggedvalue.tag = other.taggedvalue.tag;
            taggedvalue.value = other.taggedvalue.value;
            return *this;
        }
        inline value_t value()
        {
            return taggedvalue.value;
        }
        inline bool operator==(tagged_t& other)
        {
            return (taggedvalue.tag == other.taggedvalue.tag)
                && (taggedvalue.value == other.taggedvalue.value);
        }
    };
    static inline tagged_t::tag_t get_ticket(const tagged_t &p)
    {
        return p;
    }
    static inline bool set_conditional(tagged_t *p, tagged_t::value_t v,
                                       const tagged_t::tag_t& condition)
    {
        unsigned char result;
        tagged_t::value_t unused;
        __asm__ __volatile__ (
                "       push %%ebx\n\t"
                "       mov %%eax,%%ebx\n\t"
                "       inc %%ebx\n\t"
                "lock;  cmpxchg8b (%3)\n\t"
                "       setz %1\n\t"
                "       pop %%ebx\n\t"
                 : "=m"(*p), "=a"(result), "=d"(unused)
                 : "S"(p), "a"(condition.taggedvalue.tag), "d"(condition.taggedvalue.value), "c"(v)
                 : "memory", "cc"
        );
        return result;
    }
};

template<>
struct InterlockedType<1> : public InterlockedType<4>
{
};

template<>
struct InterlockedType<2> : public InterlockedType<4>
{
};


#ifdef _AMD64
template<>
struct InterlockedType<8>
{
    typedef __attribute__ ((aligned(8))) i64 value_t;
    static inline value_t fetch_and_add(value_t *p, value_t incr)
    {
        value_t old;
        __asm__ __volatile__ ("lock; xaddq %0,%1"
                      : "=r" (old), "=m" (*p)
                      : "0" (incr), "m" (*p)
                      : "memory");
        return old;
    }
    static inline value_t fetch_and_sub(value_t *p, value_t incr)
    {
        return fetch_and_add(p, -incr);
    }
    static inline value_t fetch_and_set(value_t *p, value_t v)
    {
        __asm__ __volatile__ ("lock; xchgq %2, %1"
                      : "=r" (v), "+m" (*p)
                      : "0" (v)
                      : "memory");
        return v;
    }
    static inline value_t set_conditional(value_t *p, value_t v, value_t condition)
    {
        union split {
            i64 asI64;
            i32 asI32[2];
        };
        split dst;
        split result;
        dst.asI64 = v;
        split src;
        src.asI64 = condition;

        __asm__ __volatile__ (
                "lock;  cmpxchg8b %2\n\t"
                 : "=a"(result.asI32[0]), "=d"(result.asI32[1]), "=m"(*p)
                 : "m"(*p), "a"(src.asI32[0]), "d"(src.asI32[1]),
                   "b"(dst.asI32[0]), "c"(dst.asI32[1])
                 : "memory", "cc"

        );
        return result.asI64;
    }
    static inline value_t set_and_fetch(value_t *p, value_t v)
    {
        fetch_and_set(p, v);
        return v;
    }


    struct tagged_t
    {
        typedef __attribute__ ((aligned(8))) void*  value_t;
        typedef __attribute__ ((aligned(8))) i64    counter_t;
        typedef tagged_t    tag_t;
        __attribute__ ((aligned(16))) struct
        {
            counter_t   tag;
            value_t     value;
        } taggedvalue;

        tagged_t(value_t value = 0)
        {
            taggedvalue.tag = 0;
            taggedvalue.value = value;
        }
        tagged_t(counter_t tag, value_t value)
        {
            taggedvalue.tag = tag;
            taggedvalue.value = value;
        }
        tagged_t(const tagged_t& other)
        {
            taggedvalue.tag = other.taggedvalue.tag;
            taggedvalue.value = other.taggedvalue.value;
        }
        tagged_t& operator=(const tagged_t& other)
        {
            taggedvalue.tag = other.taggedvalue.tag;
            taggedvalue.value = other.taggedvalue.value;
            return *this;
        }
        inline value_t value()
        {
            return taggedvalue.value;
        }
        inline bool operator==(tagged_t& other)
        {
            return (taggedvalue.tag == other.taggedvalue.tag)
                && (taggedvalue.value == other.taggedvalue.value);
        }
    };
    static inline tagged_t::tag_t get_ticket(const tagged_t &p)
    {
        return p;
    }
    static inline bool set_conditional(tagged_t *p, tagged_t::value_t v,
                                       const tagged_t::tag_t& condition)
    {
        unsigned char result;
        tagged_t::tag_t dummy;
        __asm__ __volatile__ (
                "\tmov %4,%%r8\n"
                "\t.byte 0xF0,0x49,0x0F,0xC7,0x08\n"
                "\tsetz %0\n"
                 : "=r"(result), "=m"(*p), "=d"(dummy.taggedvalue.value),
                   "=a"(dummy.taggedvalue.tag)
                 : "r"(p), "c"(v), "b"(condition.taggedvalue.tag+1),
                   "d"(condition.taggedvalue.value), "a"(condition.taggedvalue.tag)
                 : "memory", "cc", "r8"
        );
        return result;
    }
};
#endif


}

/**************************************************************************************************/
#endif
