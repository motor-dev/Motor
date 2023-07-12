/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#ifndef MOTOR_MINITL_SPAN_HH
#define MOTOR_MINITL_SPAN_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/initializer_list.hh>

namespace minitl {

template < typename T >
class span
{
private:
    T* const m_begin;
    T* const m_end;

public:
    typedef const T* const_iterator;
    typedef T*       iterator;

public:
    span(T* begin, T* end);
    span(T* begin, u32 count);
    span(initializer_list< T > init_list);
    span(const span& other)                = default;
    span& operator=(const span& other)     = default;
    span(span&& other) noexcept            = default;
    span& operator=(span&& other) noexcept = default;
    template < typename U >  // NOLINTNEXTLINE(google-explicit-constructor)
    span(const span< U >& other) : m_begin(other.begin())
                                 , m_end(other.end())
    {
    }
    template < typename U >
    span& operator=(const span< U >& other)
    {
        m_begin = other.m_begin;
        m_end   = other.m_end;
    }
    inline iterator       begin();
    inline iterator       end();
    inline const_iterator begin() const;
    inline const_iterator end() const;

    inline T&       operator[](u32 index);
    inline const T& operator[](u32 index) const;

    inline u32 size() const;

    T&       first();
    T&       last();
    const T& first() const;
    const T& last() const;
};

}  // namespace minitl

#include <motor/minitl/inl/span.hh>

#endif