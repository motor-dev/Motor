/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#pragma once

#include <atomic>

namespace knl {

template < unsigned size >
struct InterlockedType;

template <>
struct InterlockedType< 4 >
{
    typedef std::atomic< int > value_t;
    static inline int          fetch(const value_t* p)
    {
        return atomic_load(p);
    }
    static inline int fetch_and_add(value_t* p, int incr)
    {
        return atomic_fetch_add(p, incr);
    }
    static inline int fetch_and_sub(value_t* p, int incr)
    {
        return atomic_fetch_sub(p, incr);
    }
    static inline int fetch_and_set(value_t* p, int v)
    {
        return atomic_exchange(p, v);
    }
    static inline int set_conditional(value_t* p, int v, int condition)
    {
        if(atomic_compare_exchange_weak(p, &condition, v))
            return condition;
        else
            return v;
    }
    static inline int set_and_fetch(value_t* p, int v)
    {
        fetch_and_set(p, v);
        return v;
    }

    struct tagged_t
    {
        struct tagged_pointer
        {
            void*        value;
            unsigned int counter;
            bool         operator==(const tagged_pointer& other) const
            {
                return value == other.value && counter == other.counter;
            }
        };
        typedef std::atomic< tagged_pointer > value_t;
        typedef tagged_pointer                tag_t;

        __attribute__((aligned(4))) value_t m_value;

        tagged_t(void* value = nullptr) : m_value {tagged_pointer {value, 0}}
        {
        }
        tagged_t(const tagged_t& other) = delete;
        tagged_t& operator=(const tagged_t& other)
        {
            atomic_exchange(&m_value, atomic_load(&other.m_value));
            return *this;
        }
        inline void* value()
        {
            return atomic_load(&m_value).value;
        }
        inline bool operator==(tagged_t& other)
        {
            return atomic_load(&m_value) == atomic_load(&other.m_value);
        }
    };
    static inline tagged_t::tag_t get_ticket(const tagged_t& p)
    {
        return atomic_load(&p.m_value);
    }
    static inline bool set_conditional(tagged_t* p, void* v, tagged_t::tag_t condition)
    {
        tagged_t::tagged_pointer newValue {v, condition.counter + 1};
        return std::atomic_compare_exchange_weak(&p->m_value, &condition, newValue);
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

template <>
struct InterlockedType< 8 >
{
    typedef std::atomic< long int > value_t;
    static inline long int          fetch(const value_t* p)
    {
        return atomic_load(p);
    }
    static inline long int fetch_and_add(value_t* p, long int incr)
    {
        return atomic_fetch_add(p, incr);
    }
    static inline long int fetch_and_sub(value_t* p, long int incr)
    {
        return atomic_fetch_sub(p, incr);
    }
    static inline long int fetch_and_set(value_t* p, long int v)
    {
        return atomic_exchange(p, v);
    }
    static inline long int set_conditional(value_t* p, long int v, long int condition)
    {
        if(atomic_compare_exchange_weak(p, &condition, v))
            return condition;
        else
            return v;
    }
    static inline long int set_and_fetch(value_t* p, long int v)
    {
        fetch_and_set(p, v);
        return v;
    }

    struct tagged_t
    {
        struct tagged_pointer
        {
            void*             value;
            unsigned long int counter;
            bool              operator==(const tagged_pointer& other) const
            {
                return value == other.value && counter == other.counter;
            }
        };
        typedef std::atomic< tagged_pointer > value_t;
        typedef tagged_pointer                tag_t;

        __attribute__((aligned(8))) value_t m_value;

        tagged_t(void* value = nullptr) : m_value {tagged_pointer {value, 0}}
        {
        }
        tagged_t(const tagged_t& other) = delete;
        tagged_t& operator=(const tagged_t& other)
        {
            atomic_exchange(&m_value, other.m_value);
            return *this;
        }
        inline void* value()
        {
            return atomic_load(&m_value).value;
        }
        inline bool operator==(tagged_t& other)
        {
            return atomic_load(&m_value) == atomic_load(&other.m_value);
        }
    };
    static inline tagged_t::tag_t get_ticket(const tagged_t& p)
    {
        return atomic_load(&p.m_value);
    }
    static inline bool set_conditional(tagged_t* p, void* v, tagged_t::tag_t condition)
    {
        tagged_t::tagged_pointer newValue {v, condition.counter + 1};
        return std::atomic_compare_exchange_weak(&p->m_value, &condition, newValue);
    }
};

}  // namespace knl
