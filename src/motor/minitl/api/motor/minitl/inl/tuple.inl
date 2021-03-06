/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_INL_TUPLE_INL_
#define MOTOR_MINITL_INL_TUPLE_INL_
/**************************************************************************************************/
#include <motor/minitl/type_traits.hh>
#include <motor/minitl/utility.hh>

namespace minitl {

namespace details {

template < u32 INDEX, typename T, typename... TAIL >
struct tuple_type_at_index
{
    typedef typename tuple_type_at_index< INDEX - 1, TAIL... >::type type;
};

template < typename T, typename... TAIL >
struct tuple_type_at_index< 0, T, TAIL... >
{
    typedef T type;
};

template < int INDEX, typename T >
struct tuple_field
{
    T m_field;

    constexpr explicit tuple_field(const T& t) : m_field(t)
    {
    }
    constexpr explicit tuple_field(T&& t) : m_field(move(t))
    {
    }
    constexpr    tuple_field()                         = default;
    constexpr    tuple_field(const tuple_field& other) = default;
    constexpr    tuple_field(tuple_field&& other)      = default;
    tuple_field& operator=(const tuple_field& other)   = default;
    tuple_field& operator=(tuple_field&& other)        = default;
    ~tuple_field()                                     = default;

    constexpr T& get() &
    {
        return m_field;
    }
    constexpr const T& get() const&
    {
        return m_field;
    }
    constexpr T&& get() &&
    {
        return move(m_field);
    }
};

template < typename T >
struct tuple_field< 0, T >
{
    T first;

    constexpr explicit tuple_field(const T& t) : first(t)
    {
    }
    constexpr explicit tuple_field(T&& t) : first(move(t))
    {
    }
    constexpr    tuple_field()                         = default;
    constexpr    tuple_field(const tuple_field& other) = default;
    constexpr    tuple_field(tuple_field&& other)      = default;
    tuple_field& operator=(const tuple_field& other)   = default;
    tuple_field& operator=(tuple_field&& other)        = default;
    ~tuple_field()                                     = default;

    constexpr T& get() &
    {
        return first;
    }
    constexpr const T& get() const&
    {
        return first;
    }
    T&& get() &&
    {
        return move(first);
    }
};

template < typename T >
struct tuple_field< 1, T >
{
    T second;

    constexpr explicit tuple_field(const T& t) : second(t)
    {
    }
    constexpr explicit tuple_field(T&& t) : second(move(t))
    {
    }
    constexpr    tuple_field()                         = default;
    constexpr    tuple_field(const tuple_field& other) = default;
    constexpr    tuple_field(tuple_field&& other)      = default;
    tuple_field& operator=(const tuple_field& other)   = default;
    tuple_field& operator=(tuple_field&& other)        = default;
    ~tuple_field()                                     = default;

    constexpr T& get() &
    {
        return second;
    }
    constexpr const T& get() const&
    {
        return second;
    }
    constexpr T&& get() &&
    {
        return move(second);
    }
};

template < typename T >
struct tuple_field< 2, T >
{
    T third;

    constexpr explicit tuple_field(const T& t) : third(t)
    {
    }
    constexpr explicit tuple_field(T&& t) : third(move(t))
    {
    }
    constexpr    tuple_field()                         = default;
    constexpr    tuple_field(const tuple_field& other) = default;
    constexpr    tuple_field(tuple_field&& other)      = default;
    tuple_field& operator=(const tuple_field& other)   = default;
    tuple_field& operator=(tuple_field&& other)        = default;
    ~tuple_field()                                     = default;

    constexpr T& get() &
    {
        return third;
    }
    constexpr const T& get() const&
    {
        return third;
    }
    constexpr T&& get() &&
    {
        return move(third);
    }
};

template < int INDEX, typename T, typename... TAIL >
struct tuple_helper
    : public tuple_field< INDEX, T >
    , public tuple_helper< INDEX + 1, TAIL... >
{
    constexpr tuple_helper()                    = default;
    constexpr tuple_helper(const tuple_helper&) = default;
    constexpr tuple_helper(tuple_helper&&)      = default;
    constexpr tuple_helper(const T& t, const TAIL&... tail)
        : tuple_field< INDEX, T >(t)
        , tuple_helper< INDEX + 1, TAIL... >(tail...)
    {
    }
    template < typename T1, typename... TAIL1 >
    constexpr tuple_helper(const T1& t, const TAIL1&... tail)
        : tuple_field< INDEX, T >(t)
        , tuple_helper< INDEX + 1, TAIL... >(tail...)
    {
    }
    template < typename T1, typename... TAIL1 >
    constexpr tuple_helper(T1&& t, TAIL1&&... tail)
        : tuple_field< INDEX, T >(move(t))
        , tuple_helper< INDEX + 1, TAIL... >(move(tail)...)
    {
    }
    template < typename T1, typename... TAIL1 >
    constexpr tuple_helper(const tuple_helper< INDEX, T1, TAIL1... >& tuple)
        : tuple_field< INDEX, T >(tuple.tuple_field< INDEX, T1 >::get())
        , tuple_helper< INDEX + 1, TAIL... >((const tuple_helper< INDEX + 1, TAIL1... >&)tuple)
    {
    }
    template < typename T1, typename... TAIL1 >
    constexpr tuple_helper(tuple_helper< INDEX, T1, TAIL1... >&& tuple)
        : tuple_field< INDEX, T >(tuple.tuple_field< INDEX, T1 >::get())
        , tuple_helper< INDEX + 1, TAIL... >((const tuple_helper< INDEX + 1, TAIL1... >&)tuple)
    {
    }

    tuple_helper& operator=(const tuple_helper& other) = default;
    tuple_helper& operator=(tuple_helper&& other)      = default;
};

template < int INDEX, typename T >
struct tuple_helper< INDEX, T > : public tuple_field< INDEX, T >
{
    constexpr tuple_helper()                    = default;
    constexpr tuple_helper(const tuple_helper&) = default;
    constexpr tuple_helper(tuple_helper&&)      = default;
    constexpr tuple_helper(const T& t) : tuple_field< INDEX, T >(t)
    {
    }
    template < typename T1 >
    constexpr tuple_helper(const T1& t) : tuple_field< INDEX, T >(t)
    {
    }
    template < typename T1 >
    constexpr tuple_helper(T1&& t) : tuple_field< INDEX, T >(move(t))
    {
    }
    template < typename T1 >
    constexpr tuple_helper(const tuple_helper< INDEX, T1 >& tuple)
        : tuple_field< INDEX, T >(tuple.tuple_field< INDEX, T1 >::get())
    {
    }
    template < typename T1 >
    constexpr tuple_helper(tuple_helper< INDEX, T1 >&& tuple)
        : tuple_field< INDEX, T >(move(tuple).tuple_field< INDEX, T1 >::get())
    {
    }

    tuple_helper& operator=(const tuple_helper& other) = default;
    tuple_helper& operator=(tuple_helper&& other)      = default;
};

template < int GET, int INDEX, typename T, typename... TAIL,
           enable_if_t< GET == INDEX, bool > = false >
const T& get(const tuple_helper< INDEX, T, TAIL... >& t)
{
    return t.tuple_field< INDEX, T >::get();
}

template < int GET, int INDEX, typename T, typename... TAIL,
           enable_if_t< GET != INDEX, bool > = false >
const auto& get(const tuple_helper< INDEX, T, TAIL... >& t)
{
    return get< GET, INDEX + 1, TAIL... >(t);
}

template < int GET, int INDEX, typename T, typename... TAIL,
           enable_if_t< GET == INDEX, bool > = false >
T& get(tuple_helper< INDEX, T, TAIL... >& t)
{
    return t.tuple_field< INDEX, T >::get();
}

template < int GET, int INDEX, typename T, typename... TAIL,
           enable_if_t< GET != INDEX, bool > = false >
auto& get(tuple_helper< INDEX, T, TAIL... >& t)
{
    return get< GET, INDEX + 1, TAIL... >(t);
}

}  // namespace details

template < typename... T >
constexpr tuple< unwrap_ref_decay_t< T >... > make_tuple(T&&... args)
{
    return tuple< unwrap_ref_decay_t< T >... >(minitl::forward< T >(args)...);
}

template < int INDEX, typename... T >
auto& get(tuple< T... >& t)
{
    return details::get< INDEX >((details::tuple_helper< 0, T... >&)t);
}

template < int INDEX, typename... T >
const auto& get(const tuple< T... >& t)
{
    return details::get< INDEX >((const details::tuple_helper< 0, T... >&)t);
}

template < typename... T >
constexpr tuple< T... >::tuple(const T&... args) : details::tuple_helper< 0, T... >(args...)
{
}

template < typename... T >
template < typename... Args >
constexpr tuple< T... >::tuple(Args&&... args) : details::tuple_helper< 0, T... >(args...)
{
}

template < typename... T >
template < typename... T1 >
constexpr tuple< T... >::tuple(const tuple< T1... >& other)
    : details::tuple_helper< 0, T... >((const details::tuple_helper< 0, T1... >&)other)
{
}

template < typename... T >
template < typename... T1 >
constexpr tuple< T... >::tuple(tuple< T1... >&& other)
    : details::tuple_helper< 0, T... >((details::tuple_helper< 0, T1... > &&) other)
{
}

template < typename... T >
template < typename... T1 >
tuple< T... >& tuple< T... >::operator=(const tuple< T1... >& other)
{
    details::tuple_helper< 0, T... >::operator=((const details::tuple_helper< 0, T1... >&)other);
    return *this;
}

}  // namespace minitl

/**************************************************************************************************/
#endif
