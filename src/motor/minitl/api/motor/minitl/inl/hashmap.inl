/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_INL_HASH_MAP_INL_
#define MOTOR_MINITL_INL_HASH_MAP_INL_
/**************************************************************************************************/
#include <motor/minitl/algorithm.hh>

namespace minitl {

template < typename Key, typename Value, typename Hash >
template < typename POLICY >
struct hashmap< Key, Value, Hash >::iterator_base
{
    friend class hashmap< Key, Value, Hash >;

private:
    typedef typename POLICY::iterator iterator;

private:
    const hashmap< Key, Value, Hash >* m_owner;
    typename POLICY::iterator          m_current;

public:
    iterator_base() : m_owner(0), m_current()
    {
    }
    iterator_base(const hashmap< Key, Value, Hash >& owner, iterator l)
        : m_owner(&owner)
        , m_current(l)
    {
    }
    iterator_base(const iterator_base& other)            = default;
    iterator_base(iterator_base&& other)                 = default;
    iterator_base& operator=(const iterator_base& other) = default;
    iterator_base& operator=(iterator_base&& other)      = default;

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
    typename POLICY::reference operator*() const
    {
        return static_cast< typename POLICY::item_type* >(m_current.operator->())->value;
    }
    typename POLICY::pointer operator->() const
    {
        return &(static_cast< typename POLICY::item_type* >(m_current.operator->()))->value;
    }

    iterator_base& operator++()
    {
        do
        {
            ++m_current;
        } while((char*)m_current.   operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return *this;
    }
    iterator_base operator++(int)
    {
        iterator_base copy = *this;
        do
        {
            ++m_current;
        } while((char*)m_current.   operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return copy;
    }
    iterator_base& operator--()
    {
        do
        {
            --m_current;
        } while((char*)m_current.   operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return *this;
    }
    iterator_base operator--(int)
    {
        iterator_base copy = *this;
        do
        {
            --m_current;
        } while((char*)m_current.   operator->() >= (char*)m_owner->m_index.begin()
                && (char*)m_current.operator->() < (char*)m_owner->m_index.end());
        return copy;
    }
};

template < typename Key, typename Value, typename Hash >
struct hashmap< Key, Value, Hash >::iterator_policy
{
    typedef typename hashmap< Key, Value, Hash >::value_type    value_type;
    typedef typename hashmap< Key, Value, Hash >::value_type&   reference;
    typedef typename hashmap< Key, Value, Hash >::value_type*   pointer;
    typedef typename hashmap< Key, Value, Hash >::item          item_type;
    typedef typename hashmap< Key, Value, Hash >::list_iterator iterator;
};
template < typename Key, typename Value, typename Hash >
struct hashmap< Key, Value, Hash >::const_iterator_policy
{
    typedef const typename hashmap< Key, Value, Hash >::value_type    value_type;
    typedef const typename hashmap< Key, Value, Hash >::value_type&   reference;
    typedef const typename hashmap< Key, Value, Hash >::value_type*   pointer;
    typedef const typename hashmap< Key, Value, Hash >::item          item_type;
    typedef typename hashmap< Key, Value, Hash >::const_list_iterator iterator;
};

template < typename Key, typename Value, typename Hash >
hashmap< Key, Value, Hash >::hashmap(Allocator& allocator, u32 reserved)
    : m_itemPool(allocator, max(nextPowerOf2(reserved), u32(8)))
    , m_items()
    , m_index(allocator, 1 + max(nextPowerOf2(reserved), u32(8)))
    , m_count(0)
{
    buildIndex();
}

template < typename Key, typename Value, typename Hash >
hashmap< Key, Value, Hash >::hashmap(const hashmap& other)
    : m_itemPool(other.m_index.arena(), other.m_index.count() - 1)
    , m_items()
    , m_index(other.m_index.arena(), other.m_index.count())
    , m_count(other.m_count)
{
    buildIndex();
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

template < typename Key, typename Value, typename Hash >
hashmap< Key, Value, Hash >::hashmap(Allocator& allocator, const hashmap& other)
    : m_itemPool(allocator, other.m_index.count() - 1)
    , m_items()
    , m_index(allocator, other.m_index.count())
    , m_count(other.m_count)
{
    buildIndex();
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

template < typename Key, typename Value, typename Hash >
hashmap< Key, Value, Hash >::~hashmap()
{
    if(m_index)
    {
        for(index_item* it = m_index.begin(); it != m_index.end() - 1; ++it)
        {
            list_iterator object = it->second;
            object++;
            while(object != (it + 1)->second)
            {
                list_iterator itemToDelete = object++;
                m_itemPool.release(&static_cast< item& >(*itemToDelete));
            }
            it->~index_item();
        }
        (m_index.end() - 1)->~index_item();
    }
}

template < typename Key, typename Value, typename Hash >
void hashmap< Key, Value, Hash >::buildIndex()
{
    list_iterator current = m_items.begin();
    for(index_item* it = m_index.begin(); it != m_index.end(); ++it)
    {
        new(it) index_item;
        current = it->second = m_items.insert(current, it->first);
    }
}

template < typename Key, typename Value, typename Hash >
void hashmap< Key, Value, Hash >::grow(u32 size)
{
    motor_assert(size > m_count, "cannot resize from %d to smaller capacity %d" | m_count | size);

    size = nextPowerOf2(size);
    pool< item >                   newPool(m_index.arena(), size);
    Allocator::Block< index_item > newIndex(m_index.arena(), size + 1);
    intrusive_list< empty_item >   newList;

    list_iterator current = newList.begin();
    for(index_item* it = newIndex.begin(); it != newIndex.end(); ++it)
    {
        new(it) index_item;
        current = it->second = newList.insert(current, it->first);
    }

    for(index_item* index = m_index.begin(); index != m_index.end() - 1; ++index)
    {
        list_iterator object = index->second;
        object++;
        while(object != (index + 1)->second)
        {
            list_iterator itemToCopy = object++;
            item*         i          = static_cast< item* >(itemToCopy.operator->());
            u32           hash       = Hash()(i->value.first) % (u32)(newIndex.count() - 1);
            item*         newItem    = newPool.allocate(move(i->value));
            newList.insert(newIndex[hash].second, *newItem);
            m_itemPool.release(i);
        }
        index->~index_item();
    }
    (m_index.end() - 1)->~index_item();

    m_itemPool = move(newPool);
    m_items    = move(newList);
    m_index    = move(newIndex);
}

template < typename Key, typename Value, typename Hash >
hashmap< Key, Value, Hash >& hashmap< Key, Value, Hash >::operator=(hashmap other)
{
    swap(other);
    return *this;
}

template < typename Key, typename Value, typename Hash >
void hashmap< Key, Value, Hash >::reserve(u32 size)
{
    if(size >= m_index.count()) grow(size);
}

template < typename Key, typename Value, typename Hash >
typename hashmap< Key, Value, Hash >::iterator hashmap< Key, Value, Hash >::begin()
{
    return ++iterator(*this, m_items.begin());
}

template < typename Key, typename Value, typename Hash >
typename hashmap< Key, Value, Hash >::iterator hashmap< Key, Value, Hash >::end()
{
    return iterator(*this, m_items.end());
}

template < typename Key, typename Value, typename Hash >
typename hashmap< Key, Value, Hash >::const_iterator hashmap< Key, Value, Hash >::begin() const
{
    return ++const_iterator(*this, m_items.begin());
}

template < typename Key, typename Value, typename Hash >
typename hashmap< Key, Value, Hash >::const_iterator hashmap< Key, Value, Hash >::end() const
{
    return const_iterator(*this, m_items.end());
}

template < typename Key, typename Value, typename Hash >
u32 hashmap< Key, Value, Hash >::size() const
{
    return m_count;
}

template < typename Key, typename Value, typename Hash >
bool hashmap< Key, Value, Hash >::empty() const
{
    return m_count == 0;
}

template < typename Key, typename Value, typename Hash >
Value& hashmap< Key, Value, Hash >::operator[](const Key& key)
{
    return insert(key, Value()).first->second;
}

template < typename Key, typename Value, typename Hash >
typename hashmap< Key, Value, Hash >::iterator hashmap< Key, Value, Hash >::find(const Key& key)
{
    u32           hash = Hash()(key) % (u32)(m_index.count() - 1);
    list_iterator it   = m_index[hash].second;
    for(++it; it != m_index[hash + 1].second; ++it)
    {
        if(Hash()(static_cast< item* >(it.operator->())->value.first, key))
        {
            return iterator(*this, it);
        }
    }
    return end();
}

template < typename Key, typename Value, typename Hash >
typename hashmap< Key, Value, Hash >::const_iterator
hashmap< Key, Value, Hash >::find(const Key& key) const
{
    u32                 hash = Hash()(key) % (u32)(m_index.count() - 1);
    const_list_iterator it(const_list_iterator(m_index[hash].second.operator->()));
    const_list_iterator stop(const_list_iterator(m_index[hash + 1].second.operator->()));
    for(++it; it != stop; ++it)
    {
        if(Hash()(static_cast< const item* >(it.operator->())->value.first, key))
        {
            return const_iterator(*this, it);
        }
    }
    return end();
}

template < typename Key, typename Value, typename Hash >
typename hashmap< Key, Value, Hash >::iterator hashmap< Key, Value, Hash >::erase(iterator it)
{
    m_count--;
    item*         i = static_cast< item* >(it.m_current.operator->());
    list_iterator l = it.m_current;
    ++it;
    m_items.erase(l);
    m_itemPool.release(i);
    return it;
}

template < typename Key, typename Value, typename Hash >
void hashmap< Key, Value, Hash >::erase(const Key& key)
{
    iterator it = find(key);
    motor_assert(it != end(), "could not find item with index %s" | key);
    erase(it);
}

template < typename Key, typename Value, typename Hash >
tuple< typename hashmap< Key, Value, Hash >::iterator, bool >
hashmap< Key, Value, Hash >::insert(Key&& key, Value&& value)
{
    return insert(tuple< const Key, Value >(move(key), move(value)));
}

template < typename Key, typename Value, typename Hash >
tuple< typename hashmap< Key, Value, Hash >::iterator, bool >
hashmap< Key, Value, Hash >::insert(Key&& key, const Value& value)
{
    return insert(tuple< const Key, Value >(move(key), value));
}

template < typename Key, typename Value, typename Hash >
tuple< typename hashmap< Key, Value, Hash >::iterator, bool >
hashmap< Key, Value, Hash >::insert(const Key& key, Value&& value)
{
    return insert(tuple< const Key, Value >(key, move(value)));
}

template < typename Key, typename Value, typename Hash >
tuple< typename hashmap< Key, Value, Hash >::iterator, bool >
hashmap< Key, Value, Hash >::insert(const Key& key, const Value& value)
{
    return insert(tuple< const Key, Value >(key, value));
}

template < typename Key, typename Value, typename Hash >
tuple< typename hashmap< Key, Value, Hash >::iterator, bool >
hashmap< Key, Value, Hash >::insert(const tuple< const Key, Value >& v)
{
    return insert(tuple< const Key, Value >(v));
}

template < typename Key, typename Value, typename Hash >
tuple< typename hashmap< Key, Value, Hash >::iterator, bool >
hashmap< Key, Value, Hash >::insert(tuple< const Key, Value >&& v)
{
    u32           hash = Hash()(v.first);
    list_iterator it   = m_index[hash % (m_index.count() - 1)].second;
    for(++it; it != m_index[1 + hash % (m_index.count() - 1)].second; ++it)
    {
        if(Hash()(static_cast< item* >(it.operator->())->value.first, v.first))
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

template < typename Key, typename Value, typename Hash >
void hashmap< Key, Value, Hash >::swap(hashmap& other)
{
    m_index.swap(other.m_index);
    m_items.swap(other.m_items);
    m_itemPool.swap(other.m_itemPool);
    minitl::swap(m_count, other.m_count);
}

}  // namespace minitl

/**************************************************************************************************/
#endif
