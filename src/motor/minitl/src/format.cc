/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/minitl/format.hh>

namespace minitl { namespace format_details {

bool invalid_format(const char* reason)
{
    motor_assert_format(false, "invalid format: {0}", reason);
    return false;
}

}}  // namespace minitl::format_details
