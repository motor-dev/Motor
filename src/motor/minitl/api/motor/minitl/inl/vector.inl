/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/assert.hh>
#include <motor/minitl/utility.hh>

namespace minitl {

template < typename T >
template < typename POLICY >
class vector< T >::base_iterator
    : public random_access_iterator< T, typename vector< T >::difference_t >
{
    friend class vector< T >;

public:
    typedef random_access_iterator_tag    iterator_category_t;
    typedef typename POLICY::value_t      value_t;
    typedef typename POLICY::pointer_t    pointer_t;
    typedef typename POLICY::reference_t  reference_t;
    typedef typename POLICY::size_t       size_t;
    typedef typename POLICY::difference_t difference_t;

public:
    const vector< T >*         m_owner;
    typename POLICY::pointer_t m_iterator;

private:
    base_iterator(const vector< T >* owner, typename POLICY::pointer_t it)
        : m_owner(owner)
        , m_iterator(it)
    {
    }

public:
    base_iterator() : m_owner(0), m_iterator(0)
    {
    }

    template < typename OTHERPOLICY >
    base_iterator(const base_iterator< OTHERPOLICY >& other)  // NOLINT(google-explicit-constructor)
        : m_owner(other.m_owner)
        , m_iterator(other.m_iterator)
    {
    }

    base_iterator(const base_iterator& other)     = default;
    base_iterator(base_iterator&& other) noexcept = default;
    ~base_iterator()                              = default;

public:
    bool operator==(const base_iterator< POLICY >& other)
    {
        return m_iterator == other.m_iterator;
    }

    bool operator!=(const base_iterator< POLICY >& other)
    {
        return m_iterator != other.m_iterator;
    }
    base_iterator< POLICY >& operator=(const base_iterator< POLICY >& other)     = default;
    base_iterator< POLICY >& operator=(base_iterator< POLICY >&& other) noexcept = default;

    base_iterator< POLICY > operator+(typename POLICY::difference_t offset) const
    {
        return base_iterator< POLICY >(m_owner, POLICY::advance(m_iterator, offset));
    }
    base_iterator< POLICY > operator-(typename POLICY::difference_t offset) const
    {
        return base_iterator< POLICY >(m_owner, POLICY::advance(m_iterator, -offset));
    }
    typename POLICY::difference_t operator-(const base_iterator< POLICY >& other) const
    {
        if(motor_assert(m_owner == other.m_owner,
                        "cannot calculate distance between unrelated iterators"))
            return 0;
        return POLICY::distance(other.m_iterator, m_iterator);
    }

    base_iterator< POLICY >& operator++()
    {
        m_iterator = POLICY::advance(m_iterator, 1);
        return *this;
    }
    const base_iterator< POLICY > operator++(int)  // NOLINT(readability-const-return-type)
    {
        base_iterator< POLICY > p = *this;
        m_iterator                = POLICY::advance(m_iterator, 1);
        return p;
    }
    base_iterator< POLICY >& operator+=(typename POLICY::difference_t size)
    {
        m_iterator = POLICY::advance(m_iterator, size);
        return *this;
    }
    base_iterator< POLICY >& operator--()
    {
        m_iterator = POLICY::advance(m_iterator, -1);
        return *this;
    }
    const base_iterator< POLICY > operator--(int)  // NOLINT(readability-const-return-type)
    {
        base_iterator< POLICY > p = *this;
        m_iterator                = POLICY::advance(m_iterator, -1);
        return p;
    }
    base_iterator< POLICY >& operator-=(typename POLICY::difference_t size)
    {
        m_iterator = POLICY::advance(m_iterator, -size);
        return *this;
    }
    typename POLICY::pointer_t operator->() const
    {
        return m_iterator;
    }

    typename POLICY::reference_t operator*() const
    {
        return *m_iterator;
    }
};

template < typename T >
struct vector< T >::iterator_policy
{
    typedef typename vector< T >::value_t      value_t;
    typedef typename vector< T >::pointer_t    pointer_t;
    typedef typename vector< T >::reference_t  reference_t;
    typedef typename vector< T >::size_t       size_t;
    typedef typename vector< T >::difference_t difference_t;
    static pointer_t                           advance(pointer_t i, ptrdiff_t offset)
    {
        return minitl::advance(i, offset);
    }
    static difference_t distance(pointer_t begin, pointer_t end)
    {
        return minitl::distance(begin, end);
    }
};

template < typename T >
struct vector< T >::const_iterator_policy
{
    typedef typename vector< T >::value_t const     value_t;
    typedef typename vector< T >::const_pointer_t   pointer_t;
    typedef typename vector< T >::const_reference_t reference_t;
    typedef typename vector< T >::size_t            size_t;
    typedef typename vector< T >::difference_t      difference_t;
    static pointer_t                                advance(pointer_t i, ptrdiff_t offset)
    {
        return minitl::advance(i, offset);
    }
    static difference_t distance(pointer_t begin, pointer_t end)
    {
        return minitl::distance(begin, end);
    }
};

template < typename T >
struct vector< T >::reverse_iterator_policy
{
    typedef typename vector< T >::value_t      value_t;
    typedef typename vector< T >::pointer_t    pointer_t;
    typedef typename vector< T >::reference_t  reference_t;
    typedef typename vector< T >::size_t       size_t;
    typedef typename vector< T >::difference_t difference_t;
    static pointer_t                           advance(pointer_t i, ptrdiff_t offset)
    {
        return minitl::advance(i, -offset);
    }
    static difference_t distance(pointer_t begin, pointer_t end)
    {
        return minitl::distance(end, begin);
    }
};

template < typename T >
struct vector< T >::const_reverse_iterator_policy
{
    typedef typename vector< T >::value_t const     value_t;
    typedef typename vector< T >::const_pointer_t   pointer_t;
    typedef typename vector< T >::const_reference_t reference_t;
    typedef typename vector< T >::size_t            size_t;
    typedef typename vector< T >::difference_t      difference_t;
    static pointer_t                                advance(pointer_t i, ptrdiff_t offset)
    {
        return minitl::advance(i, -offset);
    }
    static difference_t distance(pointer_t begin, pointer_t end)
    {
        return minitl::distance(end, begin);
    }
};

template < typename T >
vector< T >::vector(allocator& allocator, size_t initial_capacity)
    : m_memory(allocator, initial_capacity)
    , m_end(m_memory)
{
}

template < typename T >
vector< T >::vector(const vector& other)
    : m_memory(other.m_memory.arena(), other.size())
    , m_end(m_memory)
{
    push_back(other.begin(), other.end());
}

template < typename T >
vector< T >::vector(vector&& other) noexcept
    : m_memory(minitl::move(other.m_memory))
    , m_end(other.m_end)
{
    other.m_end = nullptr;
}

template < typename T >
template < typename ITERATOR >
vector< T >::vector(allocator& allocator, ITERATOR first, ITERATOR last)
    : m_memory(allocator, minitl::distance(first, last))
    , m_end(m_memory)
{
    push_back(first, last);
}

template < typename T >
vector< T >& vector< T >::operator=(const vector< T >& other)
{
    if(this != &other)
    {
        clear();
        push_back(other.begin(), other.end());
    }
    return *this;
}

template < typename T >
vector< T >::~vector()
{
    for(const_pointer_t t = m_end; t > m_memory; t = advance(t, -1))
    {
        advance(t, -1)->~T();
    }
}

template < typename T >
typename vector< T >::iterator vector< T >::begin()
{
    return iterator(this, m_memory);
}

template < typename T >
typename vector< T >::iterator vector< T >::end()
{
    return iterator(this, m_end);
}

template < typename T >
typename vector< T >::const_iterator vector< T >::begin() const
{
    return const_iterator(this, m_memory);
}

template < typename T >
typename vector< T >::const_iterator vector< T >::end() const
{
    return const_iterator(this, m_end);
}

template < typename T >
typename vector< T >::reverse_iterator vector< T >::rbegin()
{
    return reverse_iterator(this, advance(m_end, -1));
}

template < typename T >
typename vector< T >::reverse_iterator vector< T >::rend()
{
    return reverse_iterator(this, advance(m_memory.data(), -1));
}

template < typename T >
typename vector< T >::const_reverse_iterator vector< T >::rbegin() const
{
    return const_reverse_iterator(this, advance(m_end, -1));
}

template < typename T >
typename vector< T >::const_reverse_iterator vector< T >::rend() const
{
    return const_reverse_iterator(this, advance(m_memory.data(), -1));
}

template < typename T >
typename vector< T >::size_t vector< T >::size() const
{
    return distance(m_memory.data(), m_end);
}

template < typename T >
bool vector< T >::empty() const
{
    return m_end == m_memory;
}

template < typename T >
typename vector< T >::reference_t vector< T >::operator[](size_t i)
{
    return *advance(m_memory.data(), i);
}

template < typename T >
typename vector< T >::const_reference_t vector< T >::operator[](size_t i) const
{
    return *advance(m_memory.data(), i);
}

template < typename T >
void vector< T >::push_back(const_reference_t r)
{
    ensure(size() + 1);
    new((void*)m_end) T(r);
    m_end = advance_ptr(m_end, 1);
}

template < typename T >
void vector< T >::push_back(rvalue_reference_t r)
{
    ensure(size() + 1);
    new((void*)m_end) T(minitl::move(r));
    m_end = advance_ptr(m_end, 1);
}

template < typename T >
template < typename ITERATOR >
void vector< T >::push_back(ITERATOR first, ITERATOR last)
{
    size_t count = minitl::distance(first, last);
    ensure(size() + count);
    while(first != last)
    {
        new((void*)m_end) T(*first);
        m_end = advance_ptr(m_end, 1);
        ++first;
    }
}

template < typename T >
typename vector< T >::iterator vector< T >::insert(const_iterator location, const_reference_t r)
{
    iterator it = ensure(location, 1);
    new(it.m_iterator) T(r);
    return it;
}

template < typename T >
typename vector< T >::iterator vector< T >::insert(const_iterator location, rvalue_reference_t r)
{
    iterator it = ensure(location, 1);
    new(it.m_iterator) T(minitl::move(r));
    return it;
}

template < typename T >
template < typename ITERATOR >
typename vector< T >::iterator vector< T >::insert(const_iterator location, ITERATOR first,
                                                   ITERATOR last)
{
    if(motor_assert(location.m_owner == this,
                    "can't insert at iterator that is not pointing on current vector"))
        return iterator(
            this, advance_ptr(m_memory.data(), distance(m_memory.data(), location.m_iterator)));

    iterator result = ensure(location, minitl::distance(first, last));

    for(iterator it = result; first != last; ++it, ++first)
        new(it.m_iterator) T(*first);

    return result;
}

template < typename T >
template < class... ARGS >
typename vector< T >::iterator vector< T >::emplace(const_iterator location, ARGS&&... args)
{
    if(motor_assert(location.m_owner == this,
                    "can't emplace at iterator that is not pointing on current vector"))
        return iterator(
            this, advance_ptr(m_memory.data(), distance(m_memory.data(), location.m_iterator)));

    iterator result = ensure(location, 1);
    new(result.m_iterator) T(minitl::forward< ARGS >(args)...);
    return result;
}

template < typename T >
template < class... ARGS >
typename vector< T >::iterator vector< T >::emplace_back(ARGS&&... args)
{
    ensure(size() + 1);
    new((void*)m_end) T(minitl::forward< ARGS >(args)...);
    iterator result(this, m_end);
    m_end = advance_ptr(m_end, 1);
    return result;
}

template < typename T >
void vector< T >::pop_back()
{
    m_end = advance_ptr(m_end, -1);
    m_end->~T();
}

template < typename T >
typename vector< T >::iterator vector< T >::erase(iterator it)
{
    return erase(it, it + 1);
}

template < typename T >
typename vector< T >::iterator vector< T >::erase(iterator first, iterator last)
{
    if(motor_assert(first.m_owner == this,
                    "can't erase iterator that is not pointing on current vector"))
        return first;
    if(motor_assert(last.m_owner == this,
                    "can't erase iterator that is not pointing on current vector"))
        return first;
    if(motor_assert_format(m_memory <= first.m_iterator && m_end > first.m_iterator,
                           "first {0} is not in the range of the vector [{1},{2})",
                           first.m_iterator, m_memory.data(), m_end))
        return first;
    if(motor_assert_format(m_memory <= last.m_iterator && m_end >= last.m_iterator,
                           "last {0} is not in the range of the vector [{1},{2})", last.m_iterator,
                           m_memory.data(), m_end))
        return first;
    if(motor_assert_format(first.m_iterator <= last.m_iterator, "first {0} is not before last {1}",
                           first.m_iterator, last.m_iterator))
        return first;

    for(pointer_t i = first.m_iterator; i != last.m_iterator; i = advance_ptr(i, 1))
    {
        i->~T();
    }
    pointer_t t  = first.m_iterator;
    pointer_t t2 = last.m_iterator;
    for(; t2 != m_end; t = advance(t, 1), t2 = advance_ptr(t2, 1))
    {
        new((void*)t) T(minitl::move(*t2));
        t2->~T();
    }
    m_end = t;
    return first;
}

template < typename T >
typename vector< T >::reference_t vector< T >::front()
{
    motor_assert(!empty(), "getting front of empty vector");
    return *m_memory;
}

template < typename T >
typename vector< T >::reference_t vector< T >::back()
{
    motor_assert(!empty(), "getting back of empty vector");
    return *advance_ptr(m_end, -1);
}

template < typename T >
typename vector< T >::const_reference_t vector< T >::front() const
{
    motor_assert(!empty(), "getting front of empty vector");
    return *m_memory;
}

template < typename T >
typename vector< T >::const_reference_t vector< T >::back() const
{
    motor_assert(!empty(), "getting front of empty vector");
    return *advance_ptr(m_end, -1);
}

template < typename T >
void vector< T >::resize(size_t size)
{
    size_t s = distance(m_memory.data(), m_end);
    if(size > s)
    {
        ensure(size);
        pointer_t newEnd = advance_ptr(m_memory.data(), size);
        for(pointer_t t = m_end; t != newEnd; ++t)
            new((void*)t) T;
        m_end = newEnd;
    }
    else
    {
        pointer_t newEnd = advance_ptr(m_memory.data(), size);
        for(pointer_t t = newEnd; t != m_end; ++t)
            t->~T();
        m_end = newEnd;
    }
}

template < typename T >
void vector< T >::clear()
{
    for(const_pointer_t t = m_end; t > m_memory; t = advance(t, -1))
    {
        advance(t, -1)->~T();
    }
    m_end = m_memory.data();
}

template < typename T >
void vector< T >::ensure(size_t size)
{
    if(size > m_memory.count())
    {
        size = size >> 1 | size;
        size = size >> 2 | size;
        size = size >> 4 | size;
        size = size >> 8 | size;
        size = size >> 16 | size;
        size++;
        reserve(size);
    }
}

template < typename T >
typename vector< T >::iterator vector< T >::ensure(const_iterator location, size_t size)
{
    size_t object_count = size;
    size += distance(m_memory.data(), m_end);
    if(size > m_memory.count())
    {
        size = size >> 1 | size;
        size = size >> 2 | size;
        size = size >> 4 | size;
        size = size >> 8 | size;
        size = size >> 16 | size;
        size++;

        allocator::block< T > block(m_memory.arena(), size);
        pointer_t             t  = block;
        pointer_t             t2 = m_memory;
        for(; t2 != location.m_iterator; t = advance_ptr(t, 1), t2 = advance_ptr(t2, 1))
        {
            new((void*)t) T(minitl::move(*t2));
            t2->~T();
        }
        iterator result(this, t);
        t = advance_ptr(t, object_count);
        for(; t2 != m_end; t = advance_ptr(t, 1), t2 = advance_ptr(t2, 1))
        {
            new((void*)t) T(minitl::move(*t2));
            t2->~T();
        }

        m_memory.swap(block);
        m_end = t;
        return result;
    }
    else
    {
        const_pointer_t end = advance_ptr(location.m_iterator, -1);
        for(pointer_t t = advance_ptr(m_end, object_count - 1), t2 = advance_ptr(m_end, -1);
            t2 != end; t = advance_ptr(t, -1), t2 = advance_ptr(t2, -1))
        {
            new((void*)t) T(minitl::move(*t2));
            t2->~T();
        }
        m_end = advance_ptr(m_end, object_count);
        return iterator(
            this, advance_ptr(m_memory.begin(), distance(m_memory.begin(), location.m_iterator)));
    }
}

template < typename T >
void vector< T >::reserve(size_t size)
{
    if(size > m_memory.count())
    {
        allocator::block< T > block(m_memory.arena(), size);
        pointer_t             t = block;
        for(pointer_t t2 = m_memory; t2 != m_end; t = advance_ptr(t, 1), t2 = advance_ptr(t2, 1))
        {
            new((void*)t) T(minitl::move(*t2));
            t2->~T();
        }
        m_memory.swap(block);
        m_end = t;
    }
}

template < typename T >
void swap(vector< T >& t1, vector< T >& t2)
{
    t1.m_memory.swap(t2.m_memory);
    swap(t1.m_end, t2.m_end);
}

}  // namespace minitl
