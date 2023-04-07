/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/features.hh>
#if MOTOR_ENABLE_ASSERT
#    include <typeinfo>
#endif

namespace minitl {

template < typename T >
scoped< T >::scoped(T* value, Allocator& allocator) : m_ptr(value)
{
    motor_assert_format(
        value->pointer::m_allocator == 0,
        "value of type {0} already has a deleter; being refcounting multiple times?",
        typeid(T).name());
    value->pointer::m_allocator = &allocator;
}

template < typename T >
scoped< T >::scoped() : m_ptr(0)
{
}

template < typename T >
scoped< T >::~scoped()
{
    if(m_ptr) m_ptr->checked_delete();
}

template < typename T >
scoped< T >::scoped(scoped&& other) : m_ptr(other.m_ptr)
{
    other.m_ptr = 0;
}

template < typename T >
template < typename U >
scoped< T >::scoped(scoped< U >&& other) : m_ptr(other.m_ptr)
{
    other.m_ptr = 0;
}

template < typename T >
template < typename U >
void scoped< T >::reset(scoped< U >&& other)
{
    if(m_ptr != other.m_ptr)
    {
        if(m_ptr)
        {
            m_ptr->checked_delete();
        }
        m_ptr       = other.m_ptr;
        other.m_ptr = 0;
    }
}

template < typename T >
T* scoped< T >::operator->() const
{
    return m_ptr;
}

template < typename T >
scoped< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool scoped< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& scoped< T >::operator*()
{
    return *m_ptr;
}

template < typename T, typename U >
bool operator==(const scoped< T >& ref1, const scoped< U >& ref2)
{
    return ref1.operator->() == ref2.operator->();
}

template < typename T, typename U >
bool operator!=(const scoped< T >& ref1, const scoped< U >& ref2)
{
    return ref1.operator->() != ref2.operator->();
}

template < typename T >
struct formatter< scoped< T > > : public format_details::default_partial_formatter< scoped< T > >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '<', ' ', 'p', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'p')
            return invalid_format("pointer formatter does not support specified format specifier");
        return true;
    }
    static u32 length(const scoped< T >& value, const format_options& options)
    {
        motor_forceuse(options);
        if(options.alternate)
            return formatter< T* >::length(value.operator->(), options);
        else
        {
            return 9 + 10 + 9;
        }
    }
    static u32 format_to(char* destination, const scoped< T >& value, const format_options& options,
                         u32 reservedLength)
    {
        const refcountable* r = value.operator->();
        if(options.alternate)
            return formatter< void* >::format_to(destination, r, options, reservedLength);
        else if(options.width == 0)
        {
#if MOTOR_ENABLE_WEAKCHECK
            return minitl::format_to(destination, reservedLength, FMT("scoped<{0:#p},{1}>"), r,
                                     r ? r->m_weakCount : 0);
#else
            return minitl::format_to(destination, reservedLength, FMT("scoped<{0:#p}>"), r);
#endif
        }
        else
        {
            char* buffer = (char*)malloca(reservedLength);
            u32   size =
#if MOTOR_ENABLE_WEAKCHECK
                minitl::format_to(buffer, reservedLength, FMT("scoped<{0:#p},{1}>"), r,
                                  r ? r->m_weakCount : 0);
#else
                minitl::format_to(buffer, reservedLength, FMT("scoped<{0:#p}>"), r);
#endif
            u32 paddingSize = size > options.width ? 0 : options.width - size;

            switch(options.align)
            {
            case '<':
                memcpy(destination, buffer, size);
                memset(destination + reservedLength, options.fill, paddingSize);
                break;
            case '>':
                memset(destination, options.fill, paddingSize);
                memcpy(destination + paddingSize, buffer, size);
                break;
            case '^':
                memset(destination, options.fill, paddingSize / 2);
                memcpy(destination + paddingSize / 2, buffer, size);
                memset(destination + paddingSize / 2 + reservedLength, options.fill,
                       paddingSize - paddingSize / 2);
                break;
            }
            freea(buffer);
            return size + paddingSize;
        }
    }
};

}  // namespace minitl
