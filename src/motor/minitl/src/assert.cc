/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <stdarg.h>
#include <stdio.h>

namespace minitl {

AssertionResult defaultAssertionCallback(const char* /*file*/, int /*line*/, const char* /*expr*/,
                                         const char* /*message*/)
{
    return AssertionResult::Break;
}

static AssertionCallback_t g_callback = defaultAssertionCallback;
AssertionCallback_t        setAssertionCallback(AssertionCallback_t callback)
{
    AssertionCallback_t previous = g_callback;
    g_callback                   = callback;
    return previous;
}

AssertionCallback_t getAssertionCallback()
{
    return g_callback;
}

}  // namespace minitl
