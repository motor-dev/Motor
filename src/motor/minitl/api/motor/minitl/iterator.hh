/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_ITERATOR_HH
#define MOTOR_MINITL_ITERATOR_HH

#include <motor/minitl/stdafx.h>
#include <stddef.h>

//! \addtogroup minitl
//! @{
namespace minitl {

typedef size_t    size_t;
typedef ptrdiff_t difference_t;

struct input_iterator_tag
{
};
struct forward_iterator_tag : public input_iterator_tag
{
};
struct bidirectional_iterator_tag : public forward_iterator_tag
{
};
struct random_access_iterator_tag : public bidirectional_iterator_tag
{
};

template < typename T, typename DIFF = ::minitl::difference_t >
struct input_iterator
{
};

template < typename T, typename DIFF = ::minitl::difference_t >
struct forward_iterator : public input_iterator< T, DIFF >
{
};

template < typename T, typename DIFF = ::minitl::difference_t >
struct bidirectional_iterator : public forward_iterator< T, DIFF >
{
};

template < typename T, typename DIFF = ::minitl::difference_t >
struct random_access_iterator : public bidirectional_iterator< T, DIFF >
{
};

template < typename ITERATOR >
struct iterator_traits
{
    typedef typename ITERATOR::iterator_category_t iterator_category_t;
    typedef typename ITERATOR::value_t             value_t;
    typedef typename ITERATOR::pointer_t           pointer_t;
    typedef typename ITERATOR::reference_t         reference_t;
    typedef typename ITERATOR::size_t              size_t;
    typedef typename ITERATOR::difference_t        difference_t;
};
template < typename T >
struct iterator_traits< T* >
{
    typedef random_access_iterator_tag iterator_category_t;
    typedef T                          value_t;
    typedef T*                         pointer_t;
    typedef T&                         reference_t;
    typedef minitl::size_t             size_t;
    typedef minitl::difference_t       difference_t;
};
template < typename T >
struct iterator_traits< const T* >
{
    typedef random_access_iterator_tag iterator_category_t;
    typedef const T                    value_t;
    typedef const T*                   pointer_t;
    typedef const T&                   reference_t;
    typedef minitl::size_t             size_t;
    typedef minitl::difference_t       difference_t;
};

template < typename ITERATOR >
static typename iterator_traits< ITERATOR >::iterator_category
iterator_category(const ITERATOR& it);

template < typename ITERATOR >
static typename iterator_traits< ITERATOR >::difference_t distance(const ITERATOR& first,
                                                                   const ITERATOR& last);

template < typename ITERATOR >
static ITERATOR advance(const ITERATOR&                                    it,
                        typename iterator_traits< ITERATOR >::difference_t offset);

template < typename CONTAINER >
typename CONTAINER::iterator begin(CONTAINER& c)
{
    return c.begin();
}

template < typename CONTAINER >
typename CONTAINER::const_iterator begin(const CONTAINER& c)
{
    return c.begin();
}

template < typename CONTAINER >
typename CONTAINER::iterator end(CONTAINER& c)
{
    return c.end();
}

template < typename CONTAINER >
typename CONTAINER::const_iterator end(const CONTAINER& c)
{
    return c.end();
}

template < typename T, size_t SIZE >
T* begin(T (&c)[SIZE])
{
    return &c[0];
}

template < typename T, size_t SIZE >
T* end(T (&c)[SIZE])
{
    return &c[SIZE];
}

}  // namespace minitl
//! @}

#include <motor/minitl/inl/iterator.hh>

#endif
