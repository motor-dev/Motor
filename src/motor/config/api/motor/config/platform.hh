/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#ifndef _WIN32
#    define OutputDebugString(s) printf("%s", s)
#endif

#ifdef _PPC

/* POWERPC ********************/
#    if defined _LITTLE_ENDIAN
#        define MOTOR_LITTLE_ENDIAN
#    else
#        define MOTOR_BIG_ENDIAN
#    endif
#    ifdef _PPC64
#        define MOTOR_64
#    else
#        define MOTOR_32
#    endif

#elif defined(_ARM)

/* ARM Big and little endian **/
#    if defined(_ARMEB)
#        define MOTOR_BIG_ENDIAN
#    elif defined(__ARMEB__)
#        define MOTOR_BIG_ENDIAN
#    else
#        define MOTOR_LITTLE_ENDIAN
#    endif

#elif defined(_X86)

/* x86 ************************/
#    define MOTOR_32
#    define MOTOR_LITTLE_ENDIAN

#elif defined(_AMD64)

/* amd64 **********************/
#    define MOTOR_64
#    define MOTOR_LITTLE_ENDIAN

/* ARM 64bits *****************/
#elif defined(_ARM64)
#    define MOTOR_64
#    define MOTOR_LITTLE_ENDIAN

#else
#    error "unknown arch"
#endif

#ifndef MOTOR_PLATFORM
#    error "Unknown platform: you need to define MOTOR_PLATFORM"
#else
// clang-format off
// NOLINTNEXTLINE(bugprone-macro-parentheses)
#    define MOTOR_PLATFORM_INCLUDE motor/config/platforms/MOTOR_PLATFORM.hh
// clang-format on
#    define MOTOR_MAKE_STRING_2(x) #x
#    define MOTOR_MAKE_STRING_1(x) MOTOR_MAKE_STRING_2(x)
#    include MOTOR_MAKE_STRING_1(MOTOR_PLATFORM_INCLUDE)
#    undef MOTOR_PLATFORM_INCLUDE
#    undef MOTOR_MAKE_STRING_1
#    undef MOTOR_MAKE_STRING_2
#endif
