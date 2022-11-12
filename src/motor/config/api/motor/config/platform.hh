/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#ifndef _WIN32
#    define OutputDebugString(s) printf("%s", s)
#endif

#ifdef _PPC

/* POWERPC ********************/
#    define MOTOR_BIGENDIAN
#    ifdef _PPC64
#        define MOTOR_64
#    else
#        define MOTOR_32
#    endif

#elif defined(_ARM)

/* ARM Big and little endian **/
#    if defined(_ARMEL)
#        define MOTOR_LITTLEENDIAN
#    else
#        define MOTOR_BIGENDIAN
#    endif

#elif defined(_X86)

/* x86 ************************/
#    define MOTOR_32
#    define MOTOR_LITTLEENDIAN

#elif defined(_AMD64)

/* amd64 **********************/
#    define MOTOR_64
#    define MOTOR_LITTLEENDIAN

/* ARM 64bits *****************/
#elif defined(_ARM64)
#    define MOTOR_64
#    define MOTOR_LITTLEENDIAN

#else
#    error "unknown arch"
#endif

#ifndef MOTOR_PLATFORM
#    error "Unknown platform: you need to define MOTOR_PLATFORM"
#else
// clang-format off
#    define MOTOR_PLATFORM_INCLUDE_ motor/config/platforms/MOTOR_PLATFORM.hh
// clang-format on
#    define MOTOR_STRINGIZE__(x) #    x
#    define MOTOR_STRINGIZE_(x)  MOTOR_STRINGIZE__(x)
#    include MOTOR_STRINGIZE_(MOTOR_PLATFORM_INCLUDE_)
#    undef MOTOR_PLATFORM_INCLUDE_
#    undef MOTOR_STRINGIZE_
#    undef MOTOR_STRINGIZE__
#endif
