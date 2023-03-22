/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TYPEINFO_FORMAT_HH_
#define MOTOR_META_TYPEINFO_FORMAT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/typeinfo.meta.hh>
#include <motor/minitl/format.hh>

namespace minitl {

template <>
struct formatter< Motor::Meta::Type > : public formatter< const char* >
{
    static u32 length(const Motor::Meta::Type& value, const format_options& options)
    {
        return formatter< const char* >::length(value.name(), options);
    }
    static u32 format_to_partial(char* destination, const Motor::Meta::Type& value,
                                 const format_options& options, u32 reservedLength,
                                 u32 maximalLength)
    {
        return formatter< const char* >::format_to_partial(destination, value.name(), options,
                                                           reservedLength, maximalLength);
    }
    static u32 format_to(char* destination, const Motor::Meta::Type& value,
                         const format_options& options, u32 reservedLength)
    {
        return formatter< const char* >::format_to(destination, value.name(), options,
                                                   reservedLength);
    }
};

}  // namespace minitl

/**************************************************************************************************/
#endif
