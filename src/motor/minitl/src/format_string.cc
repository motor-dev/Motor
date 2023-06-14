/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/format.hh>
#include <string.h>

namespace minitl { namespace format_details { namespace string_format {

motor_api(MINITL) u32 format_arg(char* destination, bool_wrapper value,
                                 const format_options& options, u32 reserved_length)
{
    motor_forceuse(options);
    if(value)
        memcpy(destination, "true", 4);   // NOLINT(bugprone-not-null-terminated-result)
    else
        memcpy(destination, "false", 5);  // NOLINT(bugprone-not-null-terminated-result)
    return reserved_length;
}

motor_api(MINITL) u32
    format_arg_partial(char* destination, bool_wrapper value, const format_options& options,
                       u32 reserved_length, u32 max_capacity)
{
    motor_forceuse(options);
    motor_forceuse(reserved_length);
    if(value)
        memcpy(destination, "true", max_capacity);
    else
        memcpy(destination, "false", max_capacity);
    return max_capacity;
}

}}}  // namespace minitl::format_details::string_format
