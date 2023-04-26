/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/allocator.hh>
#include <motor/minitl/iterator.hh>
#include <motor/minitl/swap.hh>

namespace minitl {

template < typename T >
class vector;

template < typename T >
void swap(vector< T >& t1, vector< T >& t2);

template < typename T >
class vector
{
    template < typename U >
    friend void swap(vector< U >& t1, vector< U >& t2);

private:
    template < typename POLICY >
    class base_iterator;
    struct iterator_policy;
    struct const_iterator_policy;
    struct reverse_iterator_policy;
    struct const_reverse_iterator_policy;

public:
    typedef T                    value_t;
    typedef T*                   pointer_t;
    typedef T&                   reference_t;
    typedef const T*             const_pointer_t;
    typedef const T&             const_reference_t;
    typedef T&&                  rvalue_reference_t;
    typedef minitl::size_t       size_t;
    typedef minitl::difference_t difference_t;

public:
    typedef base_iterator< iterator_policy >               iterator;
    typedef base_iterator< const_iterator_policy >         const_iterator;
    typedef base_iterator< reverse_iterator_policy >       reverse_iterator;
    typedef base_iterator< const_reverse_iterator_policy > const_reverse_iterator;

private:
    allocator::block< T > m_memory;
    T*                    m_end;

private:
    void     ensure(size_t size);
    iterator ensure(const_iterator location, size_t size);

public:
    explicit vector(allocator& allocator, size_t initial_capacity = 0);
    vector(const vector< T >& other);
    vector(vector< T >&& other) noexcept;
    vector& operator=(const vector< T >& other);
    template < typename ITERATOR >
    vector(allocator& allocator, ITERATOR first, ITERATOR last);
    ~vector();

    iterator               begin();
    iterator               end();
    const_iterator         begin() const;
    const_iterator         end() const;
    reverse_iterator       rbegin();
    reverse_iterator       rend();
    const_reverse_iterator rbegin() const;
    const_reverse_iterator rend() const;

    size_t size() const;
    bool   empty() const;

    reference_t       operator[](size_t i);
    const_reference_t operator[](size_t i) const;

    void push_back(const_reference_t r);
    void push_back(rvalue_reference_t r);
    template < typename ITERATOR >
    void push_back(ITERATOR first, ITERATOR last);
    void pop_back();

    iterator insert(const_iterator location, const_reference_t r);
    iterator insert(const_iterator location, rvalue_reference_t r);
    template < typename ITERATOR >
    iterator insert(const_iterator location, ITERATOR first, ITERATOR last);

    template < class... ARGS >
    iterator emplace(const_iterator location, ARGS&&... args);
    template < class... ARGS >
    iterator emplace_back(ARGS&&... args);

    iterator erase(iterator it);
    iterator erase(iterator first, iterator last);

    reference_t       front();
    reference_t       back();
    const_reference_t front() const;
    const_reference_t back() const;

    void reserve(size_t size);
    void resize(size_t size);
    void clear();
};

}  // namespace minitl

#include <motor/minitl/inl/vector.inl>
