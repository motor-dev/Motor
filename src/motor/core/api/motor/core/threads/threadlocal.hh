/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_THREADS_THREADLOCAL_HH_
#define MOTOR_CORE_THREADS_THREADLOCAL_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>

template < typename T >
struct tls;

namespace Motor {

class motor_api(CORE) ThreadLocal
{
    template < typename T >
    friend struct ::tls;

private:
    static void* tlsAlloc();
    static void  tlsFree(void* key);
    static void* tlsGet(void* key);
    static void  tlsSet(void* key, void* data);
};

}  // namespace Motor

template < typename T >
struct tls
{
private:
    void* m_tlsKey;

public:
    tls() : m_tlsKey(Motor::ThreadLocal::tlsAlloc())
    {
    }

    tls(const tls& other) : m_tlsKey(Motor::ThreadLocal::tlsAlloc())
    {
        *this = other;
    }

    ~tls()
    {
        Motor::ThreadLocal::tlsFree(m_tlsKey);
    }

    tls& operator=(T* t)
    {
        Motor::ThreadLocal::tlsSet(m_tlsKey, reinterpret_cast< void* >(t));
        return *this;
    }

    tls& operator=(weak< T > t)
    {
        Motor::ThreadLocal::tlsSet(m_tlsKey, reinterpret_cast< void* >(t.operator->()));
        return *this;
    }

    tls& operator=(ref< T > t)
    {
        Motor::ThreadLocal::tlsSet(m_tlsKey, reinterpret_cast< void* >(t.operator->()));
        return *this;
    }

    tls& operator=(scoped< T > t)
    {
        Motor::ThreadLocal::tlsSet(m_tlsKey, reinterpret_cast< void* >(t.operator->()));
        return *this;
    }

    operator T*()
    {
        return reinterpret_cast< T* >(Motor::ThreadLocal::tlsGet(m_tlsKey));
    }

    operator const T*() const
    {
        return reinterpret_cast< const T* >(Motor::ThreadLocal::tlsGet(m_tlsKey));
    }

    T* operator->()
    {
        return reinterpret_cast< T* >(Motor::ThreadLocal::tlsGet(m_tlsKey));
    }

    const T* operator->() const
    {
        return reinterpret_cast< const T* >(Motor::ThreadLocal::tlsGet(m_tlsKey));
    }

    operator const void*() const
    {
        return Motor::ThreadLocal::tlsGet(m_tlsKey);
    }

    bool operator!() const
    {
        return Motor::ThreadLocal::tlsGet(m_tlsKey) == 0;
    }
};

/**************************************************************************************************/
#endif
