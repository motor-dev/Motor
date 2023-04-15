/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#define __host    __host__
#define __device  __device__
#define __kernel  __device__

typedef signed char         i8;
typedef unsigned char       u8;
typedef signed short        i16;
typedef unsigned short      u16;
typedef signed int          i32;
typedef unsigned int        u32;
typedef signed long long    i64;
typedef unsigned long long  u64;
typedef u8                  byte;

#define motor_break()
#define MOTOR_NEVER_INLINE
#define MOTOR_ALWAYS_INLINE
#define MOTOR_SUPPORTS_EXCEPTIONS  0
#define MOTOR_EXPORT
#define MOTOR_IMPORT

#define motor_alignof(t)           __alignof__(t)

#define kernel_private
#define kernel_local      __shared__
#define kernel_constant   __device const
#define kernel_global     __device
#define kernel_generic
