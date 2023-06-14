/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INTRUSIVE_LIST_HH
#define MOTOR_MINITL_INTRUSIVE_LIST_HH

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
    typedef T                    value_t;
    typedef T*                   pointer_t;
    typedef T&                   reference_t;
    typedef const T*             const_pointer_t;
    typedef const T&             const_reference_t;
    typedef minitl::size_t       size_t;
    typedef minitl::difference_t difference_t;

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

    MOTOR_ALWAYS_INLINE iterator               begin();
    MOTOR_ALWAYS_INLINE iterator               end();
    MOTOR_ALWAYS_INLINE const_iterator         begin() const;
    MOTOR_ALWAYS_INLINE const_iterator         end() const;
    MOTOR_ALWAYS_INLINE reverse_iterator       rbegin();
    MOTOR_ALWAYS_INLINE reverse_iterator       rend();
    MOTOR_ALWAYS_INLINE const_reverse_iterator rbegin() const;
    MOTOR_ALWAYS_INLINE const_reverse_iterator rend() const;

    size_t                   size() const;
    MOTOR_ALWAYS_INLINE bool empty() const;

    void     push_front(const_reference_t r);
    void     push_back(const_reference_t r);
    iterator insert(iterator after, const_reference_t r);
    iterator erase(iterator it);
    iterator erase(iterator first, iterator last);

    MOTOR_ALWAYS_INLINE reference_t       front();
    MOTOR_ALWAYS_INLINE reference_t       back();
    MOTOR_ALWAYS_INLINE const_reference_t front() const;
    MOTOR_ALWAYS_INLINE const_reference_t back() const;

    MOTOR_ALWAYS_INLINE void clear();
    void                     swap(intrusive_list& other);
};

template < typename T, int INDEX >
void swap(intrusive_list< T, INDEX >& a, intrusive_list< T, INDEX >& b)
{
    a.swap(b);
}

}  // namespace minitl

#include <motor/minitl/inl/intrusive_list.hh>

#endif
