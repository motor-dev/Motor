/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_BUILTIN_HH
#define MOTOR_META_BUILTIN_HH

#include <motor/meta/stdafx.h>

namespace Motor { namespace Meta {

struct Type;

enum ClassIndex_Numeric
{
    ClassIndex_bool   = 0,
    ClassIndex_u8     = 1,
    ClassIndex_u16    = 2,
    ClassIndex_u32    = 3,
    ClassIndex_u64    = 4,
    ClassIndex_i8     = 5,
    ClassIndex_i16    = 6,
    ClassIndex_i32    = 7,
    ClassIndex_i64    = 8,
    ClassIndex_float  = 9,
    ClassIndex_double = 10
};

enum ClassIndex_String
{
    ClassIndex_istring    = 0,
    ClassIndex_inamespace = 1,
    ClassIndex_ifilename  = 2,
    ClassIndex_ipath      = 3,
    ClassIndex_text       = 4
};

motor_api(META) const Type& getTypeFromIndex(ClassIndex_Numeric index);
motor_api(META) const Type& getTypeFromIndex(ClassIndex_String index);

}}  // namespace Motor::Meta

#endif
