/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_REVERSE_HH
#define MOTOR_MINITL_INL_REVERSE_HH

#include <motor/minitl/reverse.hh>

namespace minitl {

namespace reverse_details {

template < typename T >
struct reverse_view
{
    typedef typename T::reverse_iterator iterator;

    inline iterator begin() const
    {
        return m_container.rbegin();
    }
    inline iterator end() const
    {
        return m_container.rbegin();
    }

    explicit reverse_view(T& container) : m_container(container)
    {
    }
    ~reverse_view() = default;

private:
    T& m_container;
};

template < typename T >
struct const_reverse_view
{
    typedef typename T::const_reverse_iterator iterator;

    inline iterator begin() const
    {
        return m_container.rbegin();
    }
    inline iterator end() const
    {
        return m_container.rbegin();
    }

    explicit const_reverse_view(const T& container) : m_container(container)
    {
    }
    ~const_reverse_view() = default;

private:
    const T& m_container;
};

}  // namespace reverse_details

template < typename CONTAINER >
reverse_details::reverse_view< CONTAINER > reverse_view(CONTAINER& container)
{
    return reverse_details::reverse_view< CONTAINER >(container);
}

template < typename CONTAINER >
reverse_details::const_reverse_view< CONTAINER > reverse_view(const CONTAINER& container)
{
    return reverse_details::const_reverse_view< CONTAINER >(container);
}

}  // namespace minitl

#endif
