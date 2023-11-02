/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_DEBUG_RUNTIME_CALLSTACK_HH
#define MOTOR_PLUGIN_DEBUG_RUNTIME_CALLSTACK_HH

#include <motor/plugin.debug.runtime/stdafx.h>

namespace Motor { namespace Runtime {

class motor_api(RUNTIME) Callstack
{
public:
    class motor_api(RUNTIME) Address
    {
        friend class Callstack;

    private:
        u64 m_address;

    private:
        explicit Address(const void* address);
        explicit Address(u64 address);

    public:
        Address();
        Address(const Address& other);
        ~Address() = default;
        Address& operator=(const Address& other);
        u64      address() const;
    };

public:
    static Address backtrace(size_t depth);
    static size_t  backtrace(Address * buffer, size_t count, size_t skip);
};

}}  // namespace Motor::Runtime

#endif
