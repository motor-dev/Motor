/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/algorithm.hh>

namespace minitl {

template < typename KEY, typename VALUE, typename HASH >
template < typename POLICY >
struct hashmap< KEY, VALUE, HASH >::iterator_base
{
    friend class hashmap< KEY, VALUE, HASH >;

private:
    typedef typename POLICY::iterator iterator;

private:
    const hashmap< KEY, VALUE, HASH >* m_owner;
    typename POLICY::iterator          m_current;

public:
    iterator_base() : m_owner(0), m_current()
    {
    }
    iterator_base(const hashmap< KEY, VALUE, HASH >& owner, iterator l)
        : m_owner(&owner)
        , m_current(l)
    {
    }
    iterator_base(const iterator_base& other)                = default;
    iterator_base(iterator_base&& other) noexcept            = default;
    iterator_base& operator=(const iterator_base& other)     = default;
    iterator_base& operator=(iterator_base&& other) noexcept = default;

    template < typename OTHER_POLICY >
    bool operator==(const iterator_base< OTHER_POLICY >& other) const
    {
        return m_owner == other.m_owner && m_current == other.m_current;
    }
    template < typename OTHER_POLICY >
    bool operator!=(const iterator_base< OTHER_POLICY >& other) const
    {
        return m_owner != other.m_owner || m_current != other.m_current;
    }
    typename POLICY::reference_t operator*() const
    {
        return static_cast< typename POLICY::item_t* >(m_current.operator->())->value;
    }
    typename POLICY::pointer_t operator->() const
    {
        return &(static_cast< typename POLICY::item_t* >(m_current.operator->()))->value;
    }

    iterator_base& operator++()
    {
        do
        {
            ++m_current;
        } while((char*)m_current.operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return *this;
    }
    const iterator_base operator++(int)  // NOLINT(readability-const-return-type)
    {
        iterator_base copy = *this;
        do
        {
            ++m_current;
        } while((char*)m_current.operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return copy;
    }
    iterator_base& operator--()
    {
        do
        {
            --m_current;
        } while((char*)m_current.operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return *this;
    }
    const iterator_base operator--(int)  // NOLINT(readability-const-return-type)
    {
        iterator_base copy = *this;
        do
        {
            --m_current;
        } while((char*)m_current.operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return copy;
    }
};

template < typename KEY, typename VALUE, typename HASH >
struct hashmap< KEY, VALUE, HASH >::iterator_policy
{
    typedef typename hashmap< KEY, VALUE, HASH >::value_t       value_t;
    typedef typename hashmap< KEY, VALUE, HASH >::value_t&      reference_t;
    typedef typename hashmap< KEY, VALUE, HASH >::value_t*      pointer_t;
    typedef typename hashmap< KEY, VALUE, HASH >::item          item_t;
    typedef typename hashmap< KEY, VALUE, HASH >::list_iterator iterator;
};
template < typename KEY, typename VALUE, typename HASH >
struct hashmap< KEY, VALUE, HASH >::const_iterator_policy
{
    typedef const typename hashmap< KEY, VALUE, HASH >::value_t       value_t;
    typedef const typename hashmap< KEY, VALUE, HASH >::value_t&      reference_t;
    typedef const typename hashmap< KEY, VALUE, HASH >::value_t*      pointer_t;
    typedef const typename hashmap< KEY, VALUE, HASH >::item          item_t;
    typedef typename hashmap< KEY, VALUE, HASH >::const_list_iterator iterator;
};

template < typename KEY, typename VALUE, typename HASH >
hashmap< KEY, VALUE, HASH >::hashmap(allocator& allocator, u32 reserved)
    : m_itemPool(allocator, max(next_power_of_2(reserved), u32(8)))
    , m_items()
    , m_index(allocator, 1 + max(next_power_of_2(reserved), u32(8)))
    , m_count(0)
{
    build_index();
}

template < typename KEY, typename VALUE, typename HASH >
hashmap< KEY, VALUE, HASH >::hashmap(const hashmap& other)
    : m_itemPool(other.m_index.arena(), other.m_index.count() - 1)
    , m_items()
    , m_index(other.m_index.arena(), other.m_index.count())
    , m_count(other.m_count)
{
    build_index();
    if(m_count)
    {
        list_iterator myIt = m_items.begin();
        for(const_list_iterator it = ++other.m_items.begin(); it != other.m_items.end(); ++it)
        {
            const u8* address = reinterpret_cast< const u8* >(it.operator->());
            if(address >= reinterpret_cast< const u8* >(other.m_index.begin())
               && address < reinterpret_cast< const u8* >(other.m_index.end()))
            {
                ++myIt;
            }
            else
            {
                item* i = m_itemPool.allocate(static_cast< const item* >(it.operator->())->value);
                myIt    = m_items.insert(myIt, *i);
            }
        }
    }
}

template < typename KEY, typename VALUE, typename HASH >
hashmap< KEY, VALUE, HASH >::hashmap(allocator& allocator, const hashmap& other)
    : m_itemPool(allocator, other.m_index.count() - 1)
    , m_items()
    , m_index(allocator, other.m_index.count())
    , m_count(other.m_count)
{
    build_index();
    if(m_count)
    {
        list_iterator myIt = m_items.begin();
        for(const_list_iterator it = ++other.m_items.begin(); it != other.m_items.end(); ++it)
        {
            const u8* address = reinterpret_cast< const u8* >(it.operator->());
            if(address >= reinterpret_cast< const u8* >(other.m_index.begin())
               && address < reinterpret_cast< const u8* >(other.m_index.end()))
            {
                ++myIt;
            }
            else
            {
                item* i = m_itemPool.allocate(static_cast< const item* >(it.operator->())->value);
                myIt    = m_items.insert(myIt, *i);
            }
        }
    }
}

template < typename KEY, typename VALUE, typename HASH >
hashmap< KEY, VALUE, HASH >::~hashmap()
{
    if(m_index)
    {
        for(index_item_t* it = m_index.begin(); it != m_index.end() - 1; ++it)
        {
            list_iterator object = it->second;
            object++;
            while(object != (it + 1)->second)
            {
                list_iterator itemToDelete = object++;
                m_itemPool.release(&static_cast< item& >(*itemToDelete));
            }
            it->~index_item_t();
        }
        (m_index.end() - 1)->~index_item_t();
    }
}

template < typename KEY, typename VALUE, typename HASH >
void hashmap< KEY, VALUE, HASH >::build_index()
{
    list_iterator current = m_items.begin();
    for(index_item_t* it = m_index.begin(); it != m_index.end(); ++it)
    {
        new(it) index_item_t;
        current = it->second = m_items.insert(current, it->first);
    }
}

template < typename KEY, typename VALUE, typename HASH >
void hashmap< KEY, VALUE, HASH >::grow(u32 size)
{
    motor_assert_format(size > m_count, "cannot resize from {0} to smaller capacity {1}", m_count,
                        size);

    size = next_power_of_2(size);
    pool< item >                     newPool(m_index.arena(), size);
    allocator::block< index_item_t > newIndex(m_index.arena(), size + 1);
    intrusive_list< empty_item >     newList;

    list_iterator current = newList.begin();
    for(index_item_t* it = newIndex.begin(); it != newIndex.end(); ++it)
    {
        new(it) index_item_t;
        current = it->second = newList.insert(current, it->first);
    }

    for(index_item_t* index = m_index.begin(); index != m_index.end() - 1; ++index)
    {
        list_iterator object = index->second;
        object++;
        while(object != (index + 1)->second)
        {
            list_iterator itemToCopy = object++;
            item*         i          = static_cast< item* >(itemToCopy.operator->());
            u32           hash       = HASH()(i->value.first) % (u32)(newIndex.count() - 1);
            item*         newItem    = newPool.allocate(move(i->value));
            newList.insert(newIndex[hash].second, *newItem);
            m_itemPool.release(i);
        }
        index->~index_item_t();
    }
    (m_index.end() - 1)->~index_item_t();

    m_itemPool = move(newPool);
    m_items    = move(newList);
    m_index    = move(newIndex);
}

template < typename KEY, typename VALUE, typename HASH >
hashmap< KEY, VALUE, HASH >& hashmap< KEY, VALUE, HASH >::operator=(hashmap other)
{
    swap(other);
    return *this;
}

template < typename KEY, typename VALUE, typename HASH >
void hashmap< KEY, VALUE, HASH >::reserve(u32 size)
{
    if(size >= m_index.count()) grow(size);
}

template < typename KEY, typename VALUE, typename HASH >
typename hashmap< KEY, VALUE, HASH >::iterator hashmap< KEY, VALUE, HASH >::begin()
{
    return ++iterator(*this, m_items.begin());
}

template < typename KEY, typename VALUE, typename HASH >
typename hashmap< KEY, VALUE, HASH >::iterator hashmap< KEY, VALUE, HASH >::end()
{
    return iterator(*this, m_items.end());
}

template < typename KEY, typename VALUE, typename HASH >
typename hashmap< KEY, VALUE, HASH >::const_iterator hashmap< KEY, VALUE, HASH >::begin() const
{
    return ++const_iterator(*this, m_items.begin());
}

template < typename KEY, typename VALUE, typename HASH >
typename hashmap< KEY, VALUE, HASH >::const_iterator hashmap< KEY, VALUE, HASH >::end() const
{
    return const_iterator(*this, m_items.end());
}

template < typename KEY, typename VALUE, typename HASH >
u32 hashmap< KEY, VALUE, HASH >::size() const
{
    return m_count;
}

template < typename KEY, typename VALUE, typename HASH >
bool hashmap< KEY, VALUE, HASH >::empty() const
{
    return m_count == 0;
}

template < typename KEY, typename VALUE, typename HASH >
VALUE& hashmap< KEY, VALUE, HASH >::operator[](const KEY& key)
{
    return insert(key, VALUE()).first->second;
}

template < typename KEY, typename VALUE, typename HASH >
typename hashmap< KEY, VALUE, HASH >::iterator hashmap< KEY, VALUE, HASH >::find(const KEY& key)
{
    u32           hash = HASH()(key) % (u32)(m_index.count() - 1);
    list_iterator it   = m_index[hash].second;
    for(++it; it != m_index[hash + 1].second; ++it)
    {
        if(HASH()(static_cast< item* >(it.operator->())->value.first, key))
        {
            return iterator(*this, it);
        }
    }
    return end();
}

template < typename KEY, typename VALUE, typename HASH >
typename hashmap< KEY, VALUE, HASH >::const_iterator
hashmap< KEY, VALUE, HASH >::find(const KEY& key) const
{
    u32                 hash = HASH()(key) % (u32)(m_index.count() - 1);
    const_list_iterator it(const_list_iterator(m_index[hash].second.operator->()));
    const_list_iterator stop(const_list_iterator(m_index[hash + 1].second.operator->()));
    for(++it; it != stop; ++it)
    {
        if(HASH()(static_cast< const item* >(it.operator->())->value.first, key))
        {
            return const_iterator(*this, it);
        }
    }
    return end();
}

template < typename KEY, typename VALUE, typename HASH >
auto hashmap< KEY, VALUE, HASH >::erase(iterator it) -> iterator
{
    m_count--;
    item*         i = static_cast< item* >(it.m_current.operator->());
    list_iterator l = it.m_current;
    ++it;
    m_items.erase(l);
    m_itemPool.release(i);
    return it;
}

template < typename KEY, typename VALUE, typename HASH >
void hashmap< KEY, VALUE, HASH >::erase(const KEY& key)
{
    iterator it = find(key);
    if(motor_assert_format(it != end(), "could not find item with index {0}", key)) return;
    erase(it);
}

template < typename KEY, typename VALUE, typename HASH >
tuple< typename hashmap< KEY, VALUE, HASH >::iterator, bool >
hashmap< KEY, VALUE, HASH >::insert(KEY&& key, VALUE&& value)
{
    return insert(tuple< const KEY, VALUE >(move(key), move(value)));
}

template < typename KEY, typename VALUE, typename HASH >
tuple< typename hashmap< KEY, VALUE, HASH >::iterator, bool >
hashmap< KEY, VALUE, HASH >::insert(KEY&& key, const VALUE& value)
{
    return insert(tuple< const KEY, VALUE >(move(key), value));
}

template < typename KEY, typename VALUE, typename HASH >
tuple< typename hashmap< KEY, VALUE, HASH >::iterator, bool >
hashmap< KEY, VALUE, HASH >::insert(const KEY& key, VALUE&& value)
{
    return insert(tuple< const KEY, VALUE >(key, move(value)));
}

template < typename KEY, typename VALUE, typename HASH >
tuple< typename hashmap< KEY, VALUE, HASH >::iterator, bool >
hashmap< KEY, VALUE, HASH >::insert(const KEY& key, const VALUE& value)
{
    return insert(tuple< const KEY, VALUE >(key, value));
}

template < typename KEY, typename VALUE, typename HASH >
tuple< typename hashmap< KEY, VALUE, HASH >::iterator, bool >
hashmap< KEY, VALUE, HASH >::insert(const tuple< const KEY, VALUE >& v)
{
    return insert(tuple< const KEY, VALUE >(v));
}

template < typename KEY, typename VALUE, typename HASH >
tuple< typename hashmap< KEY, VALUE, HASH >::iterator, bool >
hashmap< KEY, VALUE, HASH >::insert(tuple< const KEY, VALUE >&& v)
{
    u32           hash = HASH()(v.first);
    list_iterator it   = m_index[hash % (m_index.count() - 1)].second;
    for(++it; it != m_index[1 + hash % (m_index.count() - 1)].second; ++it)
    {
        if(HASH()(static_cast< item* >(it.operator->())->value.first, v.first))
        {
            return make_tuple(iterator(*this, it), false);
        }
    }
    --it;
    if(m_count == m_index.count() - 1)
    {
        grow(m_count * 2);
        it = m_index[hash % (m_index.count() - 1)].second;
    }
    m_count++;
    item* i = m_itemPool.allocate(move(v));
    return make_tuple(iterator(*this, m_items.insert(it, *i)), true);
}

template < typename KEY, typename VALUE, typename HASH >
void hashmap< KEY, VALUE, HASH >::swap(hashmap& other)
{
    m_index.swap(other.m_index);
    m_items.swap(other.m_items);
    m_itemPool.swap(other.m_itemPool);
    minitl::swap(m_count, other.m_count);
}

}  // namespace minitl
