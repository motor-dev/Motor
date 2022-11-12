/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>

namespace Motor { namespace Meta {

struct motor_api(META) Documentation
{
public:
    u64       size;
    const u8* bytes;
published:
    Documentation(u64 size, const u8* gzipBytes) : size(size), bytes(gzipBytes)
    {
    }
};

}}  // namespace Motor::Meta
