/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_PTR_REFPTR_INL_
#define MOTOR_MINITL_PTR_REFPTR_INL_
/**************************************************************************************************/
#include <motor/minitl/features.hh>
#include <motor/minitl/format.hh>
#if MOTOR_ENABLE_ASSERT
#    include <typeinfo>
#endif


namespace minitl {

template < typename T >
void ref< T >::swap(ref< T >& other)
{
    T* tmpPtr   = other.operator->();
    other.m_ptr = m_ptr;
    m_ptr       = tmpPtr;
}

template < typename T >
ref< T >::ref(T* value) : m_ptr(value)
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref(T* value, Allocator& deleter) : m_ptr(value)
{
    motor_assert_format(
        value->pointer::m_allocator == 0,
        "value of type {0} already has a deleter; being refcounting multiple times?",
        typeid(T).name());
    value->pointer::m_allocator = &deleter;
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref() : m_ptr(0)
{
}

template < typename T >
ref< T >::ref(const ref& other) : m_ptr(other.operator->())
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
template < typename U >
ref< T >::ref(const ref< U > other) : m_ptr(checkIsA< T >(other.operator->()))
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
template < typename U >
ref< T >::ref(scoped< U >&& other) : m_ptr(checkIsA< T >(other.operator->()))
{
    if(m_ptr) m_ptr->addref();
    other.m_ptr = 0;
}

template < typename T >
ref< T >& ref< T >::operator=(const ref< T >& other)
{
    ref(other).swap(*this);
    return *this;
}

template < typename T >
template < typename U >
ref< T >& ref< T >::operator=(const ref< U >& other)
{
    ref(other).swap(*this);
    return *this;
}

template < typename T >
ref< T >::~ref()
{
    if(m_ptr) m_ptr->decref();
}

template < typename T >
T* ref< T >::operator->() const
{
    return static_cast< T* >(m_ptr);
}

template < typename T >
ref< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool ref< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& ref< T >::operator*()
{
    return *static_cast< T* >(m_ptr);
}

template < typename T >
void ref< T >::clear()
{
    if(m_ptr) m_ptr->decref();
    m_ptr = 0;
}

template < typename T, typename U >
bool operator==(const ref< T >& ref1, const ref< U >& ref2)
{
    return ref1.operator->() == ref2.operator->();
}

template < typename T, typename U >
bool operator!=(const ref< T >& ref1, const ref< U >& ref2)
{
    return ref1.operator->() != ref2.operator->();
}

template < typename T >
struct formatter< ref< T > > : public format_details::default_partial_formatter< ref< T > >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '<', ' ', 'p', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'p')
            return invalid_format("pointer formatter does not support specified format specifier");
        return true;
    }
    static u32 length(const ref< T >& value, const format_options& options)
    {
        motor_forceuse(options);
        if(options.alternate)
            return formatter< T* >::length(value.operator->(), options);
        else
        {
            return 7 + 10 + 9 + 9;
        }
    }
    static u32 format_to(char* destination, const ref< T >& value, const format_options& options,
                         u32 reservedLength)
    {
        const refcountable* r = value.operator->();
        if(options.alternate)
            return formatter< void* >::format_to(destination, r, options, reservedLength);
        else if(options.width == 0)
        {
#if MOTOR_ENABLE_WEAKCHECK
            return minitl::format_to(destination, reservedLength, FMT("ref<{0:#p},{1},{2}>"),
                                     r, r ? r->m_refCount : 0, r ? r->m_weakCount : 0);
#else
            return minitl::format_to(destination, reservedLength, FMT("ref<{0:#p},{1}>"), r,
                                     r ? r->m_refCount : 0);
#endif
        }
        else
        {
            char* buffer      = (char*)malloca(reservedLength);
            u32   size        = minitl::format_to(buffer, reservedLength,
                                                  FMT("ref<{0:s}>({1:p}){{{2}s,{3}w}}"), typeid(T).name(), r,
                                         r ? r->m_refCount : 0, r ? r->m_weakCount : 0);
            u32   paddingSize = size > options.width ? 0 : options.width - size;

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
