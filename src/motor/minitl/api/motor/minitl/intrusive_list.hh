/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/iterator.hh>
#include <motor/minitl/swap.hh>

namespace minitl {

template < typename T, int INDEX = 0 >
class intrusive_list
{
public:
    class item;

private:
    template < typename POLICY >
    class base_iterator;
    struct iterator_policy;
    struct const_iterator_policy;
    struct reverse_iterator_policy;
    struct const_reverse_iterator_policy;

public:
    typedef T                       value_type;
    typedef T*                      pointer;
    typedef T&                      reference;
    typedef const T*                const_pointer;
    typedef const T&                const_reference;
    typedef minitl::size_type       size_type;
    typedef minitl::difference_type difference_type;

public:
    typedef base_iterator< iterator_policy >               iterator;
    typedef base_iterator< const_iterator_policy >         const_iterator;
    typedef base_iterator< reverse_iterator_policy >       reverse_iterator;
    typedef base_iterator< const_reverse_iterator_policy > const_reverse_iterator;

private:
    item m_root;

public:
    intrusive_list();
    intrusive_list(intrusive_list&& other) noexcept;
    intrusive_list(const intrusive_list& other) = delete;
    intrusive_list& operator=(intrusive_list&& other) noexcept;
    intrusive_list& operator=(const intrusive_list& other) = delete;
    ~intrusive_list();

    iterator               begin();
    iterator               end();
    const_iterator         begin() const;
    const_iterator         end() const;
    reverse_iterator       rbegin();
    reverse_iterator       rend();
    const_reverse_iterator rbegin() const;
    const_reverse_iterator rend() const;

    size_type size() const;
    bool      empty() const;

    void     push_front(const_reference r);
    void     push_back(const_reference r);
    iterator insert(iterator after, const_reference r);
    iterator erase(iterator it);
    iterator erase(iterator first, iterator last);

    reference       front();
    reference       back();
    const_reference front() const;
    const_reference back() const;

    void clear();
    void swap(intrusive_list& other);
};

template < typename T, int INDEX >
void swap(intrusive_list< T, INDEX >& a, intrusive_list< T, INDEX >& b)
{
    a.swap(b);
}

}  // namespace minitl

#include <motor/minitl/inl/intrusive_list.inl>
