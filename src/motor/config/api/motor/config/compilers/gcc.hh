/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CONFIG_COMPILERS_GCC_HH_
#define MOTOR_CONFIG_COMPILERS_GCC_HH_
/**************************************************************************************************/

#define motor_alignof(t) __alignof__(t)
#if(defined(_X86) || defined(_AMD64))
#    if defined(sun)
#        define motor_break() __asm("int $3")
#    else
#        define motor_break() __asm("int3")
#    endif
#    include <emmintrin.h>
#    define motor_pause() _mm_pause()
#elif defined(_POWERPC)
#    define motor_break() __asm("trap")
#    define motor_pause() __asm("or 27, 27, 27")
#elif defined(_ARM64)
#    define motor_break() __asm__ volatile(".word 0xd4200000");
#    define motor_pause()
#elif defined(_ARM) && !defined(__thumb__)
#    define motor_break() __asm__ volatile(".word 0xe7f001f0");
#    define motor_pause()
#elif defined(_ARM)
#    define motor_break() __asm__ volatile(".short 0xde01");
#    define motor_pause()
#else
#    error "Breakpoint not supported on this platform"
#    define motor_break()
#    define motor_pause()
#endif

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

#if __GXX_EXPERIMENTAL_CXX0X__
#    define MOTOR_HAS_MOVE_SEMANTICS
#endif

#define override
#define MOTOR_NOINLINE     __attribute__((noinline))
#define MOTOR_ALWAYSINLINE __attribute__((always_inline))
#ifdef __EXCEPTIONS
#    define MOTOR_SUPPORTS_EXCEPTIONS 1
#else
#    define MOTOR_SUPPORTS_EXCEPTIONS 0
#endif

#ifndef __cplusplus
#    define motor_restrict restrict
#else
#    define motor_restrict __restrict
#endif

#ifndef MOTOR_STATIC
#    ifdef _WIN32
#        define MOTOR_EXPORT __declspec(dllexport)
#        define MOTOR_IMPORT __declspec(dllimport)
#    elif __GNUC__ >= 4
#        define MOTOR_EXPORT __attribute__((visibility("default")))
#        define MOTOR_IMPORT __attribute__((visibility("default")))
#    else
#        define MOTOR_EXPORT
#        define MOTOR_IMPORT
#    endif
#else
#    define MOTOR_EXPORT
#    define MOTOR_IMPORT
#endif

/**************************************************************************************************/
#endif
