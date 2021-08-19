/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_BUILTIN_SCRIPT_HH_
#define MOTOR_META_BUILTIN_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/classinfo.script.hh>

#if 0

namespace Motor
{

motor_tag(Index(Motor::Meta::ClassType_String
          + (Motor::Meta::ClassIndex_istring << 16)))
struct istring
{
};

motor_tag(Index(Motor::Meta::ClassType_String
          + (Motor::Meta::ClassIndex_inamespace << 16)))
struct inamespace
{
published:
    u32 size() const;
    const istring& operator[](u32 index) const;

    void push_back(const istring& component);
    istring pop_back();
    istring pop_front();
};

motor_tag(Index(Motor::Meta::ClassType_String
          + (Motor::Meta::ClassIndex_ifilename << 16)))
struct ifilename
{
published:
    u32 size() const;
    const istring& operator[](u32 index) const;

    void push_back(const istring& component);
    istring pop_back();
    istring pop_front();
};

motor_tag(Index(Motor::Meta::ClassType_String
          + (Motor::Meta::ClassIndex_ipath << 16)))
struct ipath
{
published:
    u32 size() const;
    const istring& operator[](u32 index) const;

    void push_back(const istring& component);
    istring pop_back();
    istring pop_front();
};

motor_tag(Index(Motor::Meta::ClassType_String
          + (Motor::Meta::ClassIndex_text << 16)))
struct text
{
published:
    u32 length() const;
};

}

#endif

/**************************************************************************************************/
#endif
