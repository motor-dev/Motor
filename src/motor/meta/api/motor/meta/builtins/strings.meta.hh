/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_BUILTINS_STRINGS_META_HH
#define MOTOR_META_BUILTINS_STRINGS_META_HH

#include <motor/meta/stdafx.h>

#if 0

namespace Motor
{

struct istring
{
};

struct inamespace
{
public:
    u32 size() const;
    const istring& operator[](u32 index) const;

    void push_back(const istring& component);
    istring pop_back();
    istring pop_front();
};

struct ifilename
{
public:
    u32 size() const;
    const istring& operator[](u32 index) const;

    void push_back(const istring& component);
    istring pop_back();
    istring pop_front();
};

struct ipath
{
public:
    u32 size() const;
    const istring& operator[](u32 index) const;

    void push_back(const istring& component);
    istring pop_back();
    istring pop_front();
};

struct text
{
public:
    u32 length() const;
};

}

#endif

#include <motor/meta/builtins/strings.meta.factory.hh>
#endif
