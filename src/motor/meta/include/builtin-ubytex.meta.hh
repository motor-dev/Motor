/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_UBYTEX_SCRIPT_HH_
#define MOTOR_META_BUILTIN_UBYTEX_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_u8 << 16)))
motor_pod ubyte2
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_u8 << 16)))
motor_pod ubyte3
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_u8 << 16)))
motor_pod ubyte4
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_u8 << 16)))
motor_pod ubyte8
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_u8 << 16)))
motor_pod ubyte16
{
    u8 operator[](u32) const;
    u8& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
