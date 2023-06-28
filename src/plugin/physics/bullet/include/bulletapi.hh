/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_PHYSICS_BULLET_BULLETAPI_HH
#define MOTOR_PLUGIN_PHYSICS_BULLET_BULLETAPI_HH

#include <stddef.h>

typedef void*(btAllocFunc)(size_t size);
typedef void(btFreeFunc)(void* memory);
typedef void*(btAlignedAllocFunc)(size_t size, int alignment);
typedef void(btAlignedFreeFunc)(void* memory);

void btAlignedAllocSetCustom(btAllocFunc* allocFunc, btFreeFunc* freeFunc);
void btAlignedAllocSetCustomAligned(btAlignedAllocFunc* allocFunc, btAlignedFreeFunc* freeFunc);

#endif
