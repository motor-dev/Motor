/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_INTRUSIVE_LIST_HH
#define MOTOR_MINITL_INL_INTRUSIVE_LIST_HH
#pragma once

#include <motor/minitl/intrusive_list.hh>

#include <motor/minitl/assert.hh>

namespace minitl {

template < typename T, int INDEX >
class intrusive_list< T, INDEX >::item
{
    friend class intrusive_list< T, INDEX >;
    friend struct intrusive_list< T, INDEX >::iterator_policy;
    friend struct intrusive_list< T, INDEX >::const_iterator_policy;
    friend struct intrusive_list< T, INDEX >::reverse_iterator_policy;
    friend struct intrusive_list< T, INDEX >::const_reverse_iterator_policy;

private:
    mutable const item* m_next;
    mutable const item* m_previous;

protected:
    item();
    ~item();
    item(item&& other) noexcept;
    item& operator=(item&& other) noexcept;
    item(const item& other);
    item& operator=(const item& other);

private:
    void insert(const item* after) const;

protected:
    bool hooked() const;
    void unhook() const;
};

template < typename T, int INDEX >
intrusive_list< T, INDEX >::item::item() : m_next(this)
                                         , m_previous(this)
{
}

template < typename T, int INDEX >
intrusive_list< T, INDEX >::item::item(item&& other) noexcept : m_next(this)
                                                              , m_previous(this)
{
    motor_forceuse(other);
}

template < typename T, int INDEX >
intrusive_list< T, INDEX >::item::item(const item& other) : m_next(this)
                                                          , m_previous(this)
{
    motor_forceuse(other);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::item&
intrusive_list< T, INDEX >::item::operator=(item&& other) noexcept
{
    motor_forceuse(other);
    return *this;
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::item&
intrusive_list< T, INDEX >::item::operator=(  // NOLINT(bugprone-unhandled-self-assignment)
    const item& other)
{
    motor_forceuse(other);
    return *this;
}

template < typename T, int INDEX >
intrusive_list< T, INDEX >::item::~item()
{
    if(motor_assert(m_next == this, "destroying item that is still in a list")) unhook();
    if(motor_assert(m_previous == this, "destroying item that is still in a list")) unhook();
}

template < typename T, int INDEX >
void intrusive_list< T, INDEX >::item::insert(const item* after) const
{
    if(motor_assert(m_next == this, "list item already belongs to a list")) return;
    if(motor_assert(m_previous == this, "list item already belongs to a list")) return;
    m_next             = after->m_next;
    m_previous         = after;
    after->m_next      = this;
    m_next->m_previous = this;
}

template < typename T, int INDEX >
bool intrusive_list< T, INDEX >::item::hooked() const
{
    return m_next != this;
}

template < typename T, int INDEX >
void intrusive_list< T, INDEX >::item::unhook() const
{
    if(motor_assert(m_next != this, "list item does not belong to a list")) return;
    if(motor_assert(m_previous != this, "list item does not belong to a list")) return;
    m_next->m_previous = m_previous;
    m_previous->m_next = m_next;
    m_next             = this;
    m_previous         = this;
}

template < typename T, int INDEX >
template < typename POLICY >
class intrusive_list< T, INDEX >::base_iterator
{
    friend class intrusive_list< T, INDEX >;

public:
    typedef bidirectional_iterator_tag      iterator_category_t;
    typedef typename POLICY::value_t        value_t;
    typedef typename POLICY::pointer_t      pointer_t;
    typedef typename POLICY::reference_t    reference_t;
    typedef typename POLICY::size_t         size_t;
    typedef typename POLICY::difference_t   difference_t;
    typedef typename POLICY::item_pointer_t item_pointer_t;

private:
    item_pointer_t m_iterator;

public:
    base_iterator() : m_iterator(0)
    {
    }

    explicit base_iterator(item_pointer_t it) : m_iterator(it)
    {
    }

    base_iterator(const base_iterator& other)            = default;
    ~base_iterator()                                     = default;
    base_iterator& operator=(const base_iterator& other) = default;

public:
    bool operator==(const base_iterator< POLICY >& other) const
    {
        return m_iterator == other.m_iterator;
    }

    bool operator!=(const base_iterator< POLICY >& other) const

    {
        return m_iterator != other.m_iterator;
    }

    base_iterator< POLICY >& operator++()
    {
        m_iterator = POLICY::next(m_iterator);
        return *this;
    }
    const base_iterator< POLICY > operator++(int)  // NOLINT(readability-const-return-type)
    {
        base_iterator< POLICY > p = *this;
        m_iterator                = POLICY::next(m_iterator);
        return p;
    }
    base_iterator< POLICY >& operator--()
    {
        m_iterator = POLICY::previous(m_iterator);
        return *this;
    }
    const base_iterator< POLICY > operator--(int)  // NOLINT(readability-const-return-type)
    {
        base_iterator< POLICY > p = *this;
        m_iterator                = POLICY::previous(m_iterator);
        return p;
    }
    typename POLICY::pointer_t operator->() const
    {
        return const_cast< typename POLICY::pointer_t >(
            static_cast< typename POLICY::const_pointer_t >(m_iterator));
    }

    typename POLICY::reference_t operator*() const
    {
        return *const_cast< typename POLICY::pointer_t >(
            static_cast< typename POLICY::const_pointer_t >(m_iterator));
    }
};

template < typename T, int INDEX >
struct intrusive_list< T, INDEX >::iterator_policy
{
    typedef typename intrusive_list< T, INDEX >::value_t               value_t;
    typedef typename intrusive_list< T, INDEX >::pointer_t             pointer_t;
    typedef typename intrusive_list< T, INDEX >::const_pointer_t       const_pointer_t;
    typedef typename intrusive_list< T, INDEX >::reference_t           reference_t;
    typedef typename intrusive_list< T, INDEX >::size_t                size_t;
    typedef typename intrusive_list< T, INDEX >::difference_t          difference_t;
    typedef typename intrusive_list< T, INDEX >::item const*           item_pointer_t;
    typedef typename intrusive_list< T, INDEX >::iterator_policy       mutable_policy_t;
    typedef typename intrusive_list< T, INDEX >::const_iterator_policy const_policy_t;

    static item_pointer_t next(item_pointer_t i)
    {
        return i->m_next;
    }
    static item_pointer_t previous(item_pointer_t i)
    {
        return i->m_previous;
    }
};

template < typename T, int INDEX >
struct intrusive_list< T, INDEX >::const_iterator_policy
{
    typedef typename intrusive_list< T, INDEX >::value_t const         value_t;
    typedef typename intrusive_list< T, INDEX >::const_pointer_t       pointer_t;
    typedef typename intrusive_list< T, INDEX >::const_pointer_t       const_pointer_t;
    typedef typename intrusive_list< T, INDEX >::const_reference_t     reference_t;
    typedef typename intrusive_list< T, INDEX >::size_t                size_t;
    typedef typename intrusive_list< T, INDEX >::difference_t          difference_t;
    typedef typename intrusive_list< T, INDEX >::item const*           item_pointer_t;
    typedef typename intrusive_list< T, INDEX >::iterator_policy       mutable_policy_t;
    typedef typename intrusive_list< T, INDEX >::const_iterator_policy const_policy_t;

    static item_pointer_t next(item_pointer_t i)
    {
        return i->m_next;
    }
    static item_pointer_t previous(item_pointer_t i)
    {
        return i->m_previous;
    }
};

template < typename T, int INDEX >
struct intrusive_list< T, INDEX >::reverse_iterator_policy
{
    typedef typename intrusive_list< T, INDEX >::value_t                       value_t;
    typedef typename intrusive_list< T, INDEX >::pointer_t                     pointer_t;
    typedef typename intrusive_list< T, INDEX >::const_pointer_t               const_pointer_t;
    typedef typename intrusive_list< T, INDEX >::reference_t                   reference_t;
    typedef typename intrusive_list< T, INDEX >::size_t                        size_t;
    typedef typename intrusive_list< T, INDEX >::difference_t                  difference_t;
    typedef typename intrusive_list< T, INDEX >::item const*                   item_pointer_t;
    typedef typename intrusive_list< T, INDEX >::reverse_iterator_policy       mutable_policy_t;
    typedef typename intrusive_list< T, INDEX >::const_reverse_iterator_policy const_policy_t;

    static item_pointer_t next(item_pointer_t i)
    {
        return i->m_previous;
    }
    static item_pointer_t previous(item_pointer_t i)
    {
        return i->m_next;
    }
};

template < typename T, int INDEX >
struct intrusive_list< T, INDEX >::const_reverse_iterator_policy
{
    typedef typename intrusive_list< T, INDEX >::value_t const                 value_t;
    typedef typename intrusive_list< T, INDEX >::const_pointer_t               pointer_t;
    typedef typename intrusive_list< T, INDEX >::const_pointer_t               const_pointer_t;
    typedef typename intrusive_list< T, INDEX >::const_reference_t             reference_t;
    typedef typename intrusive_list< T, INDEX >::size_t                        size_t;
    typedef typename intrusive_list< T, INDEX >::difference_t                  difference_t;
    typedef typename intrusive_list< T, INDEX >::item const*                   item_pointer_t;
    typedef typename intrusive_list< T, INDEX >::reverse_iterator_policy       mutable_policy_t;
    typedef typename intrusive_list< T, INDEX >::const_reverse_iterator_policy const_policy_t;

    static item_pointer_t next(item_pointer_t i)
    {
        return i->m_previous;
    }
    static item_pointer_t previous(item_pointer_t i)
    {
        return i->m_next;
    }
};

template < typename T, int INDEX >
intrusive_list< T, INDEX >::intrusive_list() : m_root()
{
}

template < typename T, int INDEX >
intrusive_list< T, INDEX >::~intrusive_list()
{
    clear();
}

template < typename T, int INDEX >
intrusive_list< T, INDEX >::intrusive_list(intrusive_list&& other) noexcept : m_root()
{
    other.m_root.m_next->m_previous = &m_root;
    other.m_root.m_previous->m_next = &m_root;
    m_root.m_next                   = other.m_root.m_next;
    m_root.m_previous               = other.m_root.m_previous;
    other.m_root.m_next             = &other.m_root;
    other.m_root.m_previous         = &other.m_root;
}

template < typename T, int INDEX >
intrusive_list< T, INDEX >& intrusive_list< T, INDEX >::operator=(intrusive_list&& other) noexcept
{
    other.m_root.m_next->m_previous = &m_root;
    other.m_root.m_previous->m_next = &m_root;
    m_root.m_next                   = other.m_root.m_next;
    m_root.m_previous               = other.m_root.m_previous;
    other.m_root.m_next             = &other.m_root;
    other.m_root.m_previous         = &other.m_root;
    return *this;
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::iterator intrusive_list< T, INDEX >::begin()
{
    return iterator(m_root.m_next);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::iterator intrusive_list< T, INDEX >::end()
{
    return iterator(&m_root);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::const_iterator intrusive_list< T, INDEX >::begin() const
{
    return const_iterator(m_root.m_next);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::const_iterator intrusive_list< T, INDEX >::end() const
{
    return const_iterator(&m_root);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::reverse_iterator intrusive_list< T, INDEX >::rbegin()
{
    return reverse_iterator(m_root.m_previous);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::reverse_iterator intrusive_list< T, INDEX >::rend()
{
    return reverse_iterator(&m_root);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::const_reverse_iterator
intrusive_list< T, INDEX >::rbegin() const
{
    return const_reverse_iterator(m_root.m_previous);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::const_reverse_iterator intrusive_list< T, INDEX >::rend() const
{
    return const_reverse_iterator(&m_root);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::size_t intrusive_list< T, INDEX >::size() const
{
    size_t size = 0;
    for(const item* t = m_root.m_next; t != m_root.m_previous; t = t->m_next)
    {
        size++;
    }
    return size;
}

template < typename T, int INDEX >
bool intrusive_list< T, INDEX >::empty() const
{
    return m_root.m_next == &m_root;
}

template < typename T, int INDEX >
void intrusive_list< T, INDEX >::push_front(const_reference_t r)
{
    static_cast< const item& >(r).insert(m_root.m_previous->m_next);
}

template < typename T, int INDEX >
void intrusive_list< T, INDEX >::push_back(const_reference_t r)
{
    static_cast< const item& >(r).insert(m_root.m_previous);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::iterator
intrusive_list< T, INDEX >::insert(typename intrusive_list< T, INDEX >::iterator after,
                                   const_reference_t                             r)
{
    static_cast< const item& >(r).insert(after.m_iterator);
    return ++after;
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::iterator intrusive_list< T, INDEX >::erase(iterator it)
{
    const item* i = it.m_iterator;
    ++it;
    i->unhook();
    return it;
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::iterator intrusive_list< T, INDEX >::erase(iterator first,
                                                                                iterator last)
{
    while(first != last)
    {
        const item* i = first.m_iterator;
        ++first;
        i->unhook();
    }
    return first;
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::reference_t intrusive_list< T, INDEX >::front()
{
    return *static_cast< T* >(m_root.m_next);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::reference_t intrusive_list< T, INDEX >::back()
{
    return *static_cast< T* >(m_root.m_previous);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::const_reference_t intrusive_list< T, INDEX >::front() const
{
    return *static_cast< const T* >(m_root.m_next);
}

template < typename T, int INDEX >
typename intrusive_list< T, INDEX >::const_reference_t intrusive_list< T, INDEX >::back() const
{
    return *static_cast< const T* >(m_root.m_previous);
}

template < typename T, int INDEX >
void intrusive_list< T, INDEX >::clear()
{
    erase(begin(), end());
}

template < typename T, int INDEX >
void intrusive_list< T, INDEX >::swap(intrusive_list< T, INDEX >& other)
{
    const item* new_next     = other.m_root.m_next;
    const item* new_previous = other.m_root.m_previous;
    if(m_root.m_next != &m_root)
    {
        other.m_root.m_next             = m_root.m_next;
        other.m_root.m_next->m_previous = &other.m_root;
        other.m_root.m_previous         = m_root.m_previous;
        other.m_root.m_previous->m_next = &other.m_root;
    }
    else
    {
        other.m_root.m_next     = &other.m_root;
        other.m_root.m_previous = &other.m_root;
    }
    if(new_next != &other.m_root)
    {
        m_root.m_next             = new_next;
        m_root.m_next->m_previous = &m_root;
        m_root.m_previous         = new_previous;
        m_root.m_previous->m_next = &m_root;
    }
    else
    {
        m_root.m_next     = &m_root;
        m_root.m_previous = &m_root;
    }
}

}  // namespace minitl

#endif
