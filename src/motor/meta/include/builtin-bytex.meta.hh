/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_BYTEX_SCRIPT_HH_
#define MOTOR_META_BUILTIN_BYTEX_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_i8 << 16)))
motor_pod byte2
{
    i8 operator[](u32) const;
    i8& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_i8 << 16)))
motor_pod byte3
{
    i8 operator[](u32) const;
    i8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_i8 << 16)))
motor_pod byte4
{
    i8 operator[](u32) const;
    i8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_i8 << 16)))
motor_pod byte8
{
    i8 operator[](u32) const;
    i8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_i8 << 16)))
motor_pod byte16
{
    i8 operator[](u32) const;
    i8& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
