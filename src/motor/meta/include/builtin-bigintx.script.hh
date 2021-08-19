/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_BIGINTX_SCRIPT_HH_
#define MOTOR_META_BUILTIN_BIGINTX_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.script.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_i64 << 16)))
motor_pod bigint2
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_i64 << 16)))
motor_pod bigint3
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_i64 << 16)))
motor_pod bigint4
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_i64 << 16)))
motor_pod bigint8
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_i64 << 16)))
motor_pod bigint16
{
    i64 operator[](u32) const;
    i64& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
