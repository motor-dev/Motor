/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/plugin.debug.runtime/callstack.hh>
#include <cstdarg>
#include <cstdio>

namespace Motor { namespace Debug {

minitl::assertion_result assertionCallback(const char* file, int line, const char* expr,
                                           const char* message)
{
    fprintf(stderr, "%s:%d Assertion failed: %s\n\t", file, line, expr);
    fprintf(stderr, "%s\n", message);

    motor_fatal_format(Logger::root(), "{0}:{1} Assertion failed: {2}\n\t{3}", file, line, expr,
                       message);

    Runtime::Callstack::Address address[128];
    size_t                      result = Runtime::Callstack::backtrace(address, 128, 1);
    fprintf(stderr, "Callstack:\n");
    for(Runtime::Callstack::Address* a = address; a < address + result; ++a)
    {
        char buffer[4096];
        minitl::format_to(buffer, sizeof(buffer), FMT("[{0: #x}]\r\n"), a->address());
        fprintf(stderr, "%s", minitl::format<>(FMT("  [{0: #x}]\n"), a->address()).c_str());
    }

    return minitl::assertion_result::breakpoint;
}

}}  // namespace Motor::Debug
