/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_REFLECTION_LOCATION_META_HH
#define MOTOR_REFLECTION_LOCATION_META_HH

#include <motor/reflection/stdafx.h>

namespace Motor { namespace Meta { namespace Parse {

struct Location
{
    u32 line;
    u32 columnStart;
    u32 columnEnd;

    void newline()
    {
        line++;
        columnStart = 0;
        columnEnd   = 1;
    }
    void update(u32 column)
    {
        columnStart = columnEnd;
        columnEnd += column;
    }
};

}}}  // namespace Motor::Meta::Parse

#include <motor/reflection/location.meta.factory.hh>
#endif
