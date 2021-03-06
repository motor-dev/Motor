/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CONFIG_COMPILERS_SYNTAX_HH_
#define MOTOR_CONFIG_COMPILERS_SYNTAX_HH_
/**************************************************************************************************/

#define motor_alignof(t) __alignof__(t)
#define motor_break()
#define motor_pause()

typedef signed char       i8;
typedef signed short      i16;
typedef signed int        i32;
typedef signed long int   i64;
typedef unsigned char     u8;
typedef unsigned short    u16;
typedef unsigned int      u32;
typedef unsigned long int u64;
typedef u8                byte;

typedef unsigned long int size_t;
typedef unsigned long int ptrdiff_t;
typedef unsigned long int intptr_t;

#ifndef __cplusplus
#    define motor_restrict restrict
#else
#    define motor_restrict __restrict
#endif

#define override
#define MOTOR_NOINLINE
#define MOTOR_ALWAYSINLINE        inline
#define MOTOR_SUPPORTS_EXCEPTIONS 1

#define MOTOR_EXPORT
#define MOTOR_IMPORT

/**************************************************************************************************/
#endif
