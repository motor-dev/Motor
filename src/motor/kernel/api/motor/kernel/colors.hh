/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_KERNEL_COLORS_HH
#define MOTOR_KERNEL_COLORS_HH

#include <motor/kernel/stdafx.h>
#include <motor/kernel/simd.hh>

namespace knl { namespace Colors {

namespace Red {
static const color32 Red = {255, 0, 0, 255};
}

namespace Blue {
static const color32 Blue = {0, 0, 255, 255};
}

namespace Yellow {
static const color32 Yellow = {255, 255, 0, 255};
}

namespace Green {
static const color32 Green = {0, 255, 0, 255};
}

static inline color32 make(u8 r, u8 g, u8 b, u8 a = 255)
{
    color32 result = {r, g, b, a};
    return result;
}

}}  // namespace knl::Colors

#endif
