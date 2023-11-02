/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.debug.runtime/stdafx.h>
#include <motor/plugin.debug.runtime/callstack.hh>

namespace Motor { namespace Runtime {

Callstack::Address::Address() : m_address(0)
{
}

Callstack::Address::Address(const void* address)
    : m_address(reinterpret_cast< decltype(m_address) >(address))
{
}

Callstack::Address::Address(u64 address) : m_address(address)
{
}

Callstack::Address::Address(const Address& other) = default;

Callstack::Address& Callstack::Address::operator=(const Address& other)
{
    if(&other != this)
    {
        m_address = other.m_address;
    }
    return *this;
}

u64 Callstack::Address::address() const
{
    return m_address;
}

MOTOR_NEVER_INLINE Callstack::Address Callstack::backtrace(size_t depth)
{
    Address result;
    backtrace(&result, 1, depth + 1);
    return result;
}

}}  // namespace Motor::Runtime
