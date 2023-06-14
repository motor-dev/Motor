/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_ALLOCATOR_HH
#define MOTOR_MINITL_ALLOCATOR_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/swap.hh>
#include <string.h>

namespace minitl {

class motor_api(MINITL) allocator
{
public:
    template < typename T >
    class block;

    allocator()                            = default;
    allocator(const allocator&)            = delete;
    allocator& operator=(const allocator&) = delete;
    allocator(allocator&&)                 = delete;
    allocator& operator=(allocator&&)      = delete;

protected:
    virtual void* internal_alloc(u64 size, u64 alignment)              = 0;
    virtual bool  internal_resize(void* ptr, u64 size)                 = 0;
    virtual void* internal_realloc(void* ptr, u64 size, u64 alignment) = 0;
    virtual void  internal_free(const void* pointer)                   = 0;
    virtual ~allocator()                                               = default;

public:
    inline void* alloc(u64 size, u64 alignment = 4);
    inline bool  resize(void* ptr, u64 size);
    inline void* realloc(void* ptr, u64 size, u64 alignment);
    inline void  free(const void* pointer);
    inline char* strdup(const char* src);
    inline char* strdup(const char* begin, const char* end);
    template < typename T >
    inline T* alloc();
};

template < typename T >
class allocator::block
{
private:
    allocator* m_allocator;
    u64        m_count;
    T*         m_data;

public:
    block(allocator& allocator, u64 count, u64 block_alignment = 4)
        : m_allocator(&allocator)
        , m_count(count)
        , m_data(count ? (T*)allocator.alloc(align(sizeof(T), motor_alignof(T)) * count,
                                             max< u64 >(block_alignment, motor_alignof(T)))
                       : 0) {};
    block(block&& other) noexcept
        : m_allocator(other.m_allocator)
        , m_count(other.m_count)
        , m_data(other.m_data)
    {
        other.m_count = 0;
        other.m_data  = nullptr;
    }
    block& operator=(block&& other) noexcept
    {
        m_allocator->free(m_data);
        m_allocator   = other.m_allocator;
        m_count       = other.m_count;
        m_data        = other.m_data;
        other.m_count = 0;
        other.m_data  = nullptr;
        return *this;
    }
    block(const block&)            = delete;
    block& operator=(const block&) = delete;
    ~block()
    {
        m_allocator->free(m_data);
    }
    inline allocator& arena() const
    {
        return *m_allocator;
    }
    T* data()
    {
        return m_data;
    }
    const T* data() const
    {
        return m_data;
    }
    operator T*()  // NOLINT(google-explicit-constructor)
    {
        return m_data;
    }
    operator const T*() const  // NOLINT(google-explicit-constructor)
    {
        return m_data;
    }
    u64 count() const
    {
        return m_count;
    }
    u64 byte_count() const
    {
        return align(sizeof(T), motor_alignof(T)) * m_count;
    }
    T* begin()
    {
        return m_data;
    }
    T* end()
    {
        return m_data + m_count;
    }
    const T* begin() const
    {
        return m_data;
    }
    const T* end() const
    {
        return m_data + m_count;
    }

    bool resize(u64 count)
    {
        u64 size = align(sizeof(T), motor_alignof(T)) * count;
        if(m_allocator->resize(m_data, size))
        {
            m_count = count;
            return true;
        }
        else
        {
            return false;
        }
    }
    void realloc(u64 count, u64 block_alignment = 4)
    {
        if(count > m_count)
        {
            u64 alignment = max< u64 >(block_alignment, motor_alignof(T));
            u64 size      = align(sizeof(T), motor_alignof(T)) * count;
            m_count       = count;
            m_data        = (T*)m_allocator->realloc(m_data, size, alignment);
        }
        else
        {
            // shrink does not realloc
            m_count = count;
            if(!count)
            {
                m_allocator->free(m_data);
                m_data = 0;
            }
        }
    }
    void swap(block< T >& other)
    {
        minitl::swap(m_allocator, other.m_allocator);
        minitl::swap(m_count, other.m_count);
        minitl::swap(m_data, other.m_data);
    }
};

void* allocator::alloc(u64 size, u64 alignment)
{
    return internal_alloc(size, alignment);
}

bool allocator::resize(void* ptr, u64 size)
{
    return internal_resize(ptr, size);
}

void* allocator::realloc(void* ptr, u64 size, u64 alignment)
{
    return internal_realloc(ptr, size, alignment);
}

void allocator::free(const void* pointer)
{
    internal_free(pointer);
}

char* allocator::strdup(const char* src)
{
    size_t s      = strlen(src);
    char*  result = static_cast< char* >(internal_alloc(s + 1, 1));
    strcpy(result, src);
    return result;
}

char* allocator::strdup(const char* begin, const char* end)
{
    size_t s      = end - begin;
    char*  result = static_cast< char* >(internal_alloc(s + 1, 1));
    strncpy(result, begin, s);
    result[s] = '\0';
    return result;
}

template < typename T >
T* allocator::alloc()
{
    return (T*)alloc(sizeof(T), motor_alignof(T));
}

template < typename T >
void swap(allocator::block< T >& a, allocator::block< T >& b)
{
    a.swap(b);
}

}  // namespace minitl

#include <new>

inline void* operator new(size_t size, minitl::allocator& allocator)
{
    return allocator.alloc(size);
}

inline void* operator new(size_t size, minitl::allocator& allocator, size_t align)
{
    return allocator.alloc(size, align);
}

inline void operator delete(void* ptr, minitl::allocator& allocator)
{
    allocator.free(ptr);
}

inline void operator delete(void* ptr, minitl::allocator& allocator, size_t /*align*/)
{
    allocator.free(ptr);
}

inline void* operator new[](size_t size, minitl::allocator& allocator)
{
    return allocator.alloc(size);
}

inline void* operator new[](size_t size, minitl::allocator& allocator, size_t align)
{
    return allocator.alloc(size, align);
}

inline void operator delete[](void* ptr, minitl::allocator& allocator)
{
    allocator.free(ptr);
}

inline void operator delete[](void* ptr, minitl::allocator& allocator, size_t /*align*/)
{
    allocator.free(ptr);
}

#endif
