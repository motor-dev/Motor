/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.debug.runtime/stdafx.h>
#include <motor/plugin.debug.runtime/callstack.hh>

namespace Motor { namespace Runtime {

Callstack::Address::Address() : m_address(0)
{
}

Callstack::Address::Address(const void* address)
#ifdef _LP64
    : m_address(reinterpret_cast< u64 >(address))
#else
    : m_address(reinterpret_cast< u32 >(address))
#endif
{
}

Callstack::Address::Address(u64 address) : m_address(address)
{
}

Callstack::Address::Address(const Address& other) : m_address(other.m_address)
{
}

Callstack::Address& Callstack::Address::operator=(const Address& other)
{
    if(&other != this)
    {
        m_address = other.m_address;
    }
    return *this;
}

Callstack::Address::~Address()
{
}

u64 Callstack::Address::address() const
{
    return m_address;
}

MOTOR_NOINLINE Callstack::Address Callstack::backtrace(size_t depth)
{
    Address result;
    backtrace(&result, 1, depth + 1);
    return result;
}

}}  // namespace Motor::Runtime
