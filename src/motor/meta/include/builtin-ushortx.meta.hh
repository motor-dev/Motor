/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_USHORTX_META_HH_
#define MOTOR_META_BUILTIN_USHORTX_META_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_u16 << 16)))
motor_pod ushort2
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_u16 << 16)))
motor_pod ushort3
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_u16 << 16)))
motor_pod ushort4
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_u16 << 16)))
motor_pod ushort8
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_u16 << 16)))
motor_pod ushort16
{
    u16 operator[](u32) const;
    u16& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
