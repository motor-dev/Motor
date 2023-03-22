/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_INL_WEAKPTR_INL_
#define MOTOR_MINITL_INL_WEAKPTR_INL_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/minitl/refptr.hh>
#include <motor/minitl/scopedptr.hh>

namespace minitl {

template < typename T >
void weak< T >::swap(weak& other)
{
    T* tmp      = other.m_ptr;
    other.m_ptr = m_ptr;
    m_ptr       = tmp;
}

template < typename T >
weak< T >::weak() : m_ptr(0)
{
}

template < typename T >
weak< T >::weak(T* p) : m_ptr(p)
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->addweak();
#endif
}

template < typename T >
template < typename U >
weak< T >::weak(ref< U > other) : m_ptr(checkIsA< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->addweak();
#endif
}

template < typename T >
template < typename U >
weak< T >::weak(const scoped< U >& other) : m_ptr(checkIsA< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->addweak();
#endif
}

template < typename T >
weak< T >::weak(const weak& other) : m_ptr(other.operator->())
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->addweak();
#endif
}

template < typename T >
template < typename U >
weak< T >::weak(const weak< U >& other) : m_ptr(checkIsA< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->addweak();
#endif
}

template < typename T >
weak< T >::~weak()
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->decweak();
#endif
}

template < typename T >
weak< T >& weak< T >::operator=(const weak& other)
{
    weak(other).swap(*this);
    return *this;
}

template < typename T >
template < typename U >
weak< T >& weak< T >::operator=(const weak< U >& other)
{
    weak(other).swap(*this);
    return *this;
}

template < typename T >
template < typename U >
weak< T >& weak< T >::operator=(U* other)
{
    weak(other).swap(*this);
    return *this;
}

template < typename T >
T* weak< T >::operator->() const
{
    return static_cast< T* >(m_ptr);
}

template < typename T >
weak< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool weak< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& weak< T >::operator*()
{
    return *static_cast< T* >(m_ptr);
}

template < typename T >
void weak< T >::clear()
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->decweak();
#endif
    m_ptr = 0;
}

template < typename T >
struct formatter< weak< T > > : public format_details::default_partial_formatter< weak< T > >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '<', ' ', 'p', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'p')
            return invalid_format("pointer formatter does not support specified format specifier");
        return true;
    }
    static u32 length(const weak< T >& value, const format_options& options)
    {
        motor_forceuse(options);
        if(options.alternate)
            return formatter< T* >::length(value.operator->(), options);
        else
        {
            return 8 + 10 + 9;
        }
    }
    static u32 format_to(char* destination, const weak< T >& value, const format_options& options,
                         u32 reservedLength)
    {
        const pointer* r = value.operator->();
        if(options.alternate)
            return formatter< void* >::format_to(destination, r, options, reservedLength);
        else if(options.width == 0)
        {
#if MOTOR_ENABLE_WEAKCHECK
            return minitl::format_to(destination, reservedLength, FMT("weak<{0:#p},{1}>"), r,
                                     r ? r->m_weakCount : 0);
#else
            return minitl::format_to(destination, reservedLength, FMT("weak<{0:#p}>"), r);
#endif
        }
        else
        {
            char* buffer = (char*)malloca(reservedLength);
            u32   size =
#if MOTOR_ENABLE_WEAKCHECK
                minitl::format_to(buffer, reservedLength, FMT("weak<{0:#p},{1}>"), r,
                                  r ? r->m_weakCount : 0);
#else
                minitl::format_to(buffer, reservedLength, FMT("weak<{0:#p}>"), r);
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

/**************************************************************************************************/
#endif
