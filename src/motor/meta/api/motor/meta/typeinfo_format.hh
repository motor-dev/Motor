/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TYPEINFO_FORMAT_HH_
#define MOTOR_META_TYPEINFO_FORMAT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/typeinfo.meta.hh>
#include <motor/minitl/format.hh>

namespace Motor { namespace Meta {

motor_api(META) u32 format_length(const Type& type, const minitl::format_options& options);
motor_api(META) u32 format_arg(char* destination, const Type& type,
                               const minitl::format_options& options, u32 reservedLength);
motor_api(META) u32
    format_arg_partial(char* destination, const Type& type, const minitl::format_options& options,
                       u32 reservedLength, u32 maxCapacity);

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
