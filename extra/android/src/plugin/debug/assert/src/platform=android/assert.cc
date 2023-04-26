/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/minitl/assert.hh>
#include <cstdarg>
#include <cstdio>

namespace Motor { namespace Debug {

minitl::assertion_result assertionCallback(const char* file, int line, const char* expr,
                                           const char* message)
{
    fprintf(stderr, "%s:%d Assertion failed: %s\n\t", file, line, expr);
    fprintf(stderr, "%s\n", message);

    return minitl::assertion_result::breakpoint;
}

}}  // namespace Motor::Debug
