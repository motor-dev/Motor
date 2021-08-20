/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_DOUBLEX_SCRIPT_HH_
#define MOTOR_META_BUILTIN_DOUBLEX_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.meta.hh>

#if 0
namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_Vector2
          + (Motor::Meta::ClassIndex_double << 16)))
motor_pod double2
{
    double operator[](u32) const;
    double& operator[](u32);
};


motor_tag(Index(Motor::Meta::ClassType_Vector3
          + (Motor::Meta::ClassIndex_double << 16)))
motor_pod double3
{
    double operator[](u32) const;
    double& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector4
          + (Motor::Meta::ClassIndex_double << 16)))
motor_pod double4
{
    double operator[](u32) const;
    double& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector8
          + (Motor::Meta::ClassIndex_double << 16)))
motor_pod double8
{
    double operator[](u32) const;
    double& operator[](u32);
};

motor_tag(Index(Motor::Meta::ClassType_Vector16
          + (Motor::Meta::ClassIndex_double << 16)))
motor_pod double16
{
    double operator[](u32) const;
    double& operator[](u32);
};

}
#endif

/**************************************************************************************************/
#endif
