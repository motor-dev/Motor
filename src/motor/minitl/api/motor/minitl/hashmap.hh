/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_HASHMAP_HH
#define MOTOR_MINITL_HASHMAP_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/iterator.hh>
#include <motor/minitl/pool.hh>
#include <motor/minitl/swap.hh>
#include <motor/minitl/traits.hh>
#include <motor/minitl/tuple.hh>

namespace minitl {

template < typename KEY, typename VALUE, typename HASH = hash< KEY > >
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

    typedef tuple< const KEY, VALUE >        value_t;
    typedef tuple< const KEY, VALUE >&       reference_t;
    typedef const tuple< const KEY, VALUE >& const_reference_t;

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
        value_t value;
        explicit item(const value_t& value) : value(value)
        {
        }
        explicit item(value_t&& value) : value(minitl::move(value))
        {
        }
    };
    typedef typename intrusive_list< empty_item >::iterator       list_iterator;
    typedef typename intrusive_list< empty_item >::const_iterator const_list_iterator;
    typedef tuple< empty_item, list_iterator >                    index_item_t;

private:
    pool< item >                     m_itemPool;
    intrusive_list< empty_item >     m_items;
    allocator::block< index_item_t > m_index;
    u32                              m_count;

private:
    void build_index();
    void grow(u32 size);

public:
    explicit hashmap(allocator& allocator, u32 reserved = 0);
    ~hashmap();
    hashmap(const hashmap& other);
    hashmap(hashmap&& other) = default;  // NOLINT(performance-noexcept-move-constructor)
    hashmap(allocator& allocator, const hashmap& other);
    hashmap& operator=(hashmap&& other) = default;  // NOLINT(performance-noexcept-move-constructor)
    hashmap& operator=(hashmap other);

    void reserve(u32 size);

    iterator       begin();
    iterator       end();
    const_iterator begin() const;
    const_iterator end() const;

    u32  size() const;
    bool empty() const;

    VALUE& operator[](const KEY& key);

    iterator       find(const KEY& key);
    const_iterator find(const KEY& key) const;

    iterator erase(iterator it);
    void     erase(const KEY& key);

    tuple< iterator, bool > insert(KEY&& k, VALUE&& value);
    tuple< iterator, bool > insert(KEY&& k, const VALUE& value);
    tuple< iterator, bool > insert(const KEY& k, VALUE&& value);
    tuple< iterator, bool > insert(const KEY& k, const VALUE& value);
    tuple< iterator, bool > insert(const tuple< const KEY, VALUE >& v);
    tuple< iterator, bool > insert(tuple< const KEY, VALUE >&& v);

    void swap(hashmap& other);
};

template < typename KEY, typename VALUE, typename HASH = hash< KEY > >
void swap(hashmap< KEY, VALUE, HASH >& a, hashmap< KEY, VALUE, HASH >& b)
{
    a.swap(b);
}

}  // namespace minitl

#include <motor/minitl/inl/hashmap.hh>

#endif
