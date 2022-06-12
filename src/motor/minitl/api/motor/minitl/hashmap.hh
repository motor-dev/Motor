/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_HASHMAP_HH_
#define MOTOR_MINITL_HASHMAP_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/iterator.hh>
#include <motor/minitl/pool.hh>
#include <motor/minitl/swap.hh>
#include <motor/minitl/traits.hh>
#include <motor/minitl/tuple.hh>

namespace minitl {

template < typename Key, typename Value, typename Hash = hash< Key > >
class hashmap
{
private:
    template < typename POLICY >
    struct iterator_base;

    struct iterator_policy;
    struct reverse_iterator_policy;
    struct const_iterator_policy;
    struct const_reverse_iterator_policy;

public:
    typedef iterator_base< iterator_policy >       iterator;
    typedef iterator_base< const_iterator_policy > const_iterator;

    typedef tuple< const Key, Value >        value_type;
    typedef tuple< const Key, Value >&       reference;
    typedef const tuple< const Key, Value >& const_reference;

private:
    struct empty_item : public intrusive_list< empty_item >::item
    {
        ~empty_item()
        {
            if(this->hooked()) this->unhook();
        }
    };
    struct item : public empty_item
    {
        value_type value;
        item(const value_type& value) : value(value)
        {
        }
        item(value_type&& value) : value(move(value))
        {
        }
    };
    typedef typename intrusive_list< empty_item >::iterator       list_iterator;
    typedef typename intrusive_list< empty_item >::const_iterator const_list_iterator;
    typedef tuple< empty_item, list_iterator >                    index_item;

private:
    pool< item >                   m_itemPool;
    intrusive_list< empty_item >   m_items;
    Allocator::Block< index_item > m_index;
    u32                            m_count;

private:
    void buildIndex();
    void grow(u32 size);

public:
    hashmap(Allocator& allocator, u32 reserved = 0);
    ~hashmap();
    hashmap(const hashmap& other);
    hashmap(hashmap&& other) = default;
    hashmap(Allocator& allocator, const hashmap& other);
    hashmap& operator=(hashmap&& other) = default;
    hashmap& operator=(hashmap other);

    void reserve(u32 size);

    iterator       begin();
    iterator       end();
    const_iterator begin() const;
    const_iterator end() const;

    u32  size() const;
    bool empty() const;

    Value& operator[](const Key& key);

    iterator       find(const Key& key);
    const_iterator find(const Key& key) const;

    iterator erase(iterator it);
    void     erase(const Key& key);

    tuple< iterator, bool > insert(Key&& k, Value&& value);
    tuple< iterator, bool > insert(Key&& k, const Value& value);
    tuple< iterator, bool > insert(const Key& k, Value&& value);
    tuple< iterator, bool > insert(const Key& k, const Value& value);
    tuple< iterator, bool > insert(const tuple< const Key, Value >& v);
    tuple< iterator, bool > insert(tuple< const Key, Value >&& v);

    void swap(hashmap& other);
};

template < typename Key, typename Value, typename Hash = hash< Key > >
void swap(hashmap< Key, Value, Hash >& a, hashmap< Key, Value, Hash >& b)
{
    a.swap(b);
}

}  // namespace minitl

#include <motor/minitl/inl/hashmap.inl>

/**************************************************************************************************/
#endif
