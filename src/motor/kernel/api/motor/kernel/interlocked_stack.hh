/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/kernel/stdafx.h>
#include <motor/kernel/interlocked.hh>

namespace knl {

template < typename T >
struct itaggedptr
{
private:
    typedef InterlockedType< sizeof(T*) > impl;
    typedef typename impl::tagged_t       type_t;
    typedef typename type_t::value_t      value_t;

private:
    type_t m_value {};

public:
    itaggedptr(T* t = nullptr)  // NOLINT(google-explicit-constructor)
        : m_value((typename type_t::value_t)(t))
    {
    }
    typedef typename type_t::tag_t ticket_t;

    operator const T*() const  // NOLINT(google-explicit-constructor)
    {
        return static_cast< T* >(m_value.value());
    }
    operator T*()  // NOLINT(google-explicit-constructor)
    {
        return static_cast< T* >(m_value.value());
    }
    T* operator->()
    {
        return static_cast< T* >(m_value.value());
    }
    const T* operator->() const
    {
        return static_cast< T* >(m_value.value());
    }

    ticket_t getTicket()
    {
        return impl::get_ticket(m_value);
    }
    bool setConditional(T* value, const ticket_t& condition)
    {
        return impl::set_conditional(&m_value, reinterpret_cast< value_t >(value), condition);
    }
};

template < typename T >
class istack
{
public:
    struct node
    {
        T* next;
        node() : next(0)
        {
        }
        node(const node& /*other*/) : next(0)
        {
        }
    };

private:
    itaggedptr< node > m_head;

public:
    istack();
    istack(istack&& other)            = default;  // NOLINT(performance-noexcept-move-constructor)
    istack& operator=(istack&& other) = default;  // NOLINT(performance-noexcept-move-constructor)
    ~istack()                         = default;

    istack(const istack& other)            = delete;
    istack& operator=(const istack& other) = delete;

    void push(T* item);
    void pushList(T* head, T* tail);
    T*   pop();
    T*   popAll();
};

template < typename T >
istack< T >::istack() : m_head()
{
}

template < typename T >
void istack< T >::push(T* item)
{
    return pushList(item, item);
}

template < typename T >
void istack< T >::pushList(T* head, T* tail)
{
    typename itaggedptr< node >::ticket_t ticket;
    do
    {
        ticket     = m_head.getTicket();
        tail->next = static_cast< T* >(ticket.value());
    } while(!m_head.setConditional(head, ticket));
}

template < typename T >
T* istack< T >::pop()
{
    typename itaggedptr< node >::ticket_t ticket;
    T*                                    result;
    do
    {
        ticket = m_head.getTicket();
        result = static_cast< T* >(ticket.value());
    } while(result && !m_head.setConditional(result->next, ticket));
    return result;
}

template < typename T >
T* istack< T >::popAll()
{
    typename itaggedptr< node >::ticket_t ticket;
    T*                                    result;
    do
    {
        ticket = m_head.getTicket();
        result = static_cast< T* >(ticket.value());
    } while(result && !m_head.setConditional(0, ticket));
    return result;
}

}  // namespace knl
