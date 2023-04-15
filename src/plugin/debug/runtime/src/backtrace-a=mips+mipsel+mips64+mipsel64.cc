/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.debug.runtime/stdafx.h>
#include <motor/plugin.debug.runtime/callstack.hh>

namespace Motor { namespace Runtime {

MOTOR_NEVER_INLINE size_t Callstack::backtrace(Address* /*buffer*/, size_t /*count*/,
                                               size_t /*skip*/)
{
    motor_warning("backtrace not implemented for MIPS");
    return 0;
}

}}  // namespace Motor::Runtime
