/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <cstddef>

//! \addtogroup minitl
//! @{
namespace minitl {

typedef std::size_t    size_t;
typedef std::ptrdiff_t difference_t;

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

#include <motor/minitl/assert.hh>

namespace minitl {

namespace details {

template < typename ITERATOR, typename ITERATOR_TYPE >
static typename iterator_traits< ITERATOR >::difference_t
distance(const ITERATOR& t1, const ITERATOR& t2, ITERATOR_TYPE /*type*/)
{
    typename ITERATOR::difference_t result = 0;
    while(t1 != t2)
    {
        result++;
        ++t1;
    }
    return result;
}

template < typename ITERATOR >
static typename iterator_traits< ITERATOR >::difference_t
distance(const ITERATOR& t1, const ITERATOR& t2, random_access_iterator_tag /*type*/)
{
    return t2 - t1;
}

}  // namespace details

template < typename ITERATOR >
typename iterator_traits< ITERATOR >::iterator_category_t iterator_category(const ITERATOR& /*it*/)
{
    return typename iterator_traits< ITERATOR >::iterator_category_t();
}

template < typename ITERATOR >
typename iterator_traits< ITERATOR >::difference_t distance(const ITERATOR& first,
                                                            const ITERATOR& last)
{
    return details::distance(first, last, iterator_category(first));
}

template < typename T >
difference_t distance(T* t1, T* t2)
{
    const byte* ptr1 = reinterpret_cast< const byte* >(t1);
    const byte* ptr2 = reinterpret_cast< const byte* >(t2);
    ptrdiff_t   d    = ptr2 - ptr1;
    motor_assert_format(d % minitl::align(sizeof(T), motor_alignof(T)) == 0,
                        "distance between {0} and {1} is not a multiple of the size", t1, t2);
    return d / minitl::align(sizeof(T), motor_alignof(T));
}

template < typename T >
difference_t distance(const T* t1, const T* t2)
{
    const byte* ptr1 = reinterpret_cast< const byte* >(t1);
    const byte* ptr2 = reinterpret_cast< const byte* >(t2);
    ptrdiff_t   d    = ptr2 - ptr1;
    motor_assert_format(d % align(sizeof(T), motor_alignof(T)) == 0,
                        "distance between {0} and {1} is not a multiple of the size", t1, t2);
    return d / align(sizeof(T), motor_alignof(T));
}

template < typename ITERATOR >
static ITERATOR advance(const ITERATOR&                                    it,
                        typename iterator_traits< ITERATOR >::difference_t offset)
{
    return it + offset;
}

template < typename T >
static T* advance_ptr(T* input, difference_t offset)
{
    char* ptr = reinterpret_cast< char* >(input);
    ptr       = ptr + minitl::align(sizeof(T), motor_alignof(T)) * offset;
    return reinterpret_cast< T* >(ptr);
}

template < typename T >
static const T* advance_ptr(const T* input, difference_t offset)
{
    const char* ptr = reinterpret_cast< const char* >(input);
    ptr             = ptr + minitl::align(sizeof(T), motor_alignof(T)) * offset;
    return reinterpret_cast< const T* >(ptr);
}

}  // namespace minitl
