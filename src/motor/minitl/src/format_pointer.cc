/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/format.hh>
#include <string.h>

namespace minitl { namespace format_details { namespace pointer_format {

motor_api(MINITL) u32
    format_arg(char* destination, const void* pointer, const format_options& options)
{
    union
    {
        const void* pointer;
        u64         number;
    } x          = {pointer};
    u32 result   = options.alternate;
    *destination = '@';
    destination += result;
#if _LP64
    result += hexadecimal_format::format_hexadecimal_whole(destination + result, x.number);
#else
    result += hexadecimal_format::format_hexadecimal_whole(destination + result, u32(x.number));
#endif
    return result;
}

}}}  // namespace minitl::format_details::pointer_format
