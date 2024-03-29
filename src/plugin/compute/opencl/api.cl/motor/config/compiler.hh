/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CONFIG_COMPILER_HH
#define MOTOR_CONFIG_COMPILER_HH

#define __host    // NOLINT(bugprone-reserved-identifier)
#define __device  // NOLINT(bugprone-reserved-identifier)

typedef signed char    i8;
typedef unsigned char  u8;
typedef signed short   i16;
typedef unsigned short u16;
typedef signed int     i32;
typedef unsigned int   u32;
typedef signed long    i64;
typedef unsigned long  u64;
typedef u8             byte;

#define motor_break()
#define override
#define MOTOR_NEVER_INLINE
#define MOTOR_ALWAYS_INLINE
#define MOTOR_SUPPORTS_EXCEPTIONS 0
#define MOTOR_EXPORT
#define MOTOR_IMPORT

#define kernel_private  __private
#define kernel_local    __local
#define kernel_constant __constant
#define kernel_global   __global
#define kernel_generic  __generic

#define kernel
#define __kernel  // NOLINT(bugprone-reserved-identifier)

#define motor_alignof(t) __alignof__(t)

#pragma OPENCL EXTENSION cl_khr_int64_base_atomics : enable
#include <opencl-c.h>

#endif
