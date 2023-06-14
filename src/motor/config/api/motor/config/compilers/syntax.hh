/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CONFIG_COMPILERS_SYNTAX_HH
#define MOTOR_CONFIG_COMPILERS_SYNTAX_HH

#define motor_alignof(t) __alignof__(t)
#define motor_break()
#define motor_pause()

#include <stdint.h>
#include <stdlib.h>
typedef char                   i8;
typedef short                  i16;
typedef int                    i32;
typedef long long int          i64;
typedef unsigned char          u8;
typedef unsigned short         u16;
typedef unsigned int           u32;
typedef unsigned long long int u64;
typedef u8                     byte;
#ifndef __cplusplus
#    define motor_restrict restrict
#else
#    define motor_restrict __restrict
#endif

#define MOTOR_NEVER_INLINE
#define MOTOR_ALWAYS_INLINE       inline
#define MOTOR_SUPPORTS_EXCEPTIONS 1
#define MOTOR_COMPILER_CLANG      1

#define MOTOR_EXPORT
#define MOTOR_IMPORT

#endif
