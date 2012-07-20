/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_MINITL_HASHMAP_HH_
#define BE_MINITL_HASHMAP_HH_
/*****************************************************************************/
#include    <minitl/pair.hh>
#include    <minitl/traits.hh>
#include    <minitl/iterator.hh>
#include    <map>

namespace minitl
{

template< typename T >
struct hash;


template< typename Key, typename Value, typename Hash = std::less<Key> >
class hashmap : public std::map<Key, Value, Hash>
{
public:
    hashmap(BugEngine::Allocator& allocator, size_type reserved = 0);
    ~hashmap();
};
/*{
private:
    template< typename POLICY > class base_iterator;
    struct iterator_policy;
    struct const_iterator_policy;
    struct reverse_iterator_policy;
    struct const_reverse_iterator_policy;
public:
    typedef minitl::pair<const Key, Value>          value_type;
    typedef minitl::pair<const Key, Value>*         pointer;
    typedef minitl::pair<const Key, Value>&         reference;
    typedef const minitl::pair<const Key, Value>*   const_pointer;
    typedef const minitl::pair<const Key, Value>&   const_reference;
    typedef minitl::size_type                       size_type;
    typedef minitl::difference_type                 difference_type;
public:
    typedef base_iterator<iterator_policy>                  iterator;
    typedef base_iterator<const_iterator_policy>            const_iterator;
    typedef base_iterator<reverse_iterator_policy>          reverse_iterator;
    typedef base_iterator<const_reverse_iterator_policy>    const_reverse_iterator;
private:
    minitl::pool<value_type>                    m_objects;
    BugEngine::Allocator::Block<value_type*>    m_hashes;
    size_type                                   m_size;
    size_type                                   m_capacity;
public:
    hashmap(BugEngine::Allocator& allocator, size_type reserved = 0);
    ~hashmap();

    void                            reserve(size_type size);

    iterator                        begin();
    iterator                        end();
    const_iterator                  begin() const;
    const_iterator                  end() const;
    reverse_iterator                rbegin();
    reverse_iterator                rend();
    const_reverse_iterator          rbegin() const;
    const_reverse_iterator          rend() const;

    size_type                       size() const;
    bool                            empty() const;

    reference                       operator[](const Key& key);
    const_reference                 operator[](const Key& key) const;

    iterator                        find(const Key& key);
    const_iterator                  find(const Key& key) const;

    void                            erase(iterator it);

    minitl::pair<iterator, bool>    insert(const Key& k, const Value& value);
    minitl::pair<iterator, bool>    insert(const minitl::pair<const Key, Value>& v);
};*/

}

#include    <minitl/inl/hash_map.inl>

/*****************************************************************************/
#endif