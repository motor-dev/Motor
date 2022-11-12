/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#define motor_alignof(t) __alignof__(t)
#if defined(_X86) || defined(_AMD64)
#    define motor_break() asm("int $3")
#    include <emmintrin.h>
#    define motor_pause() _mm_pause()
#else
#    error Platform not supported
#endif

#include <alloca.h>
#include <stdint.h>
#include <stdlib.h>
typedef int8_t   i8;
typedef int16_t  i16;
typedef int32_t  i32;
typedef int64_t  i64;
typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef u8       byte;

#ifndef __cplusplus
#    define motor_restrict restrict
#else
#    define motor_restrict __restrict
#endif

#ifndef alloca
#    define alloca(x) __builtin_alloca(x)
extern "C" void* __builtin_alloca(size_t);
#endif
#ifdef __EXCEPTIONS
#    define MOTOR_SUPPORTS_EXCEPTIONS 1
#else
#    define MOTOR_SUPPORTS_EXCEPTIONS 0
#endif

#undef __REDIRECT
#ifdef __Cplusplus
#    include <cerrno>
#else
#    include <errno.h>
#endif

#define MOTOR_NOINLINE
#define MOTOR_ALWAYSINLINE inline

#define MOTOR_EXPORT __global
#define MOTOR_IMPORT

#pragma error_messages(off, noexthrow)
#if __SUNPRO_CC < 0x5130
#    pragma error_messages(off, wbadinit)
#    pragma error_messages(off, wbadasg)
#elif __SUNPRO_CC < 0x5140
#    pragma error_messages(off, wbadlkginit)
#endif
#if __SUNPRO_CC >= 0x5130
#    pragma error_messages(off, arrowrtn2)
#endif
#if __SUNPRO_CC >= 0x5140 && __SUNPRO_CC < 0x5150
#    pragma error_messages(off, placementdelmatch)
#endif
