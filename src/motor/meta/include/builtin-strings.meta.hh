/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_BUILTIN_STRINGS_META_HH
#define MOTOR_META_BUILTIN_STRINGS_META_HH

#include <motor/meta/stdafx.h>

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
public:
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
public:
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
public:
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
public:
    u32 length() const;
};

}

#endif

#endif
