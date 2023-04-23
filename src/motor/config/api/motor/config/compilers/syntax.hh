/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#define motor_alignof(t) __alignof__(t)
#define motor_break()
#define motor_pause()

#include <cstdint>
#include <cstdlib>
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

#define MOTOR_NEVER_INLINE
#define MOTOR_ALWAYS_INLINE       inline
#define MOTOR_SUPPORTS_EXCEPTIONS 1

#define MOTOR_EXPORT
#define MOTOR_IMPORT
