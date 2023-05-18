/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#if defined(__INTEL_COMPILER)
#    define MOTOR_COMPILER_INTEL 1
#    define MOTOR_COMPILER_NAME  "intel"
#    include <motor/config/compilers/intel.hh>
#elif defined(_MSC_VER)
#    define MOTOR_COMPILER_MSVC 1
#    define MOTOR_COMPILER_NAME "msvc"
#    include <motor/config/compilers/msvc.hh>
#elif defined(__SUNPRO_C) || defined(__SUNPRO_CC)
#    define MOTOR_COMPILER_SUNCC 1
#    define MOTOR_COMPILER_NAME  "suncc"
#    include <motor/config/compilers/suncc.hh>
#elif defined(__clang__)
#    define MOTOR_COMPILER_CLANG 1
#    define MOTOR_COMPILER_NAME  "clang"
#    include <motor/config/compilers/clang.hh>
#elif defined(__GNUC__)
#    define MOTOR_COMPILER_GCC  1
#    define MOTOR_COMPILER_NAME "gcc"
#    include <motor/config/compilers/gcc.hh>
#elif defined(__clang_analyzer__)
#    include <motor/config/compilers/syntax.hh>
#else
#    error unsupported compiler
#    include <motor/config/compilers/syntax.hh>
#endif

#ifdef __host
#    undef __host
#endif
#define __host  // NOLINT(bugprone-reserved-identifier)
#ifdef __device
#    undef __device
#endif
#define __device  // NOLINT(bugprone-reserved-identifier)
#ifdef __kernel
#    undef __kernel
#endif
#define __kernel  // NOLINT(bugprone-reserved-identifier)

#define kernel_constant const
#define kernel_global
#define kernel_local
#define kernel_private
#define kernel_generic

#if defined(__clang_analyzer__)
#    define MOTOR_FILE "dummy"
#    define MOTOR_LINE 0
#else
#    define MOTOR_FILE __FILE__
#    define MOTOR_LINE __LINE__
#endif
