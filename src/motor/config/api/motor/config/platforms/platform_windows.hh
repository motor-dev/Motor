/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CONFIG_PLATFORMS_PLATFORM_WIN32_HH_
#define MOTOR_CONFIG_PLATFORMS_PLATFORM_WIN32_HH_
/**************************************************************************************************/

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

#ifdef _AMD64
#    define MOTOR_PLATFORM_NAME  Win64
#    define MOTOR_PLATFORM_WIN64 1
#else
#    define MOTOR_PLATFORM_NAME Win32
#endif
#define MOTOR_PLATFORM_WIN32 1
#define MOTOR_PLATFORM_PC    1

#include <stdlib.h>
#ifdef _MSC_VER
#    include <malloc.h>
#    define malloca  _alloca
#    define freea(p) (void)p
#else
#    include <malloc.h>
#    define malloca  alloca
#    define freea(p) (void)p
#endif

/**************************************************************************************************/
#endif
