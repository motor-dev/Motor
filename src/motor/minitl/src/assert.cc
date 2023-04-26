/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>

namespace minitl {

assertion_result default_assertion_callback(const char* /*file*/, int /*line*/,
                                            const char* /*expr*/, const char* /*message*/)
{
    return assertion_result::breakpoint;
}

static assertion_callback_t g_callback = default_assertion_callback;
assertion_callback_t        set_assertion_callback(assertion_callback_t callback)
{
    assertion_callback_t previous = g_callback;
    g_callback                    = callback;
    return previous;
}

assertion_callback_t get_assertion_callback()
{
    return g_callback;
}

}  // namespace minitl
