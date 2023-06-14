/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CONFIG_COMPILER_HH
#define MOTOR_CONFIG_COMPILER_HH

#if defined(__clang_analyzer__)
#    include <motor/config/compilers/syntax.hh>
#elif defined(__INTEL_COMPILER)
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
#elif defined(__GNUC__) && !defined(__clang__)
#    define MOTOR_COMPILER_GCC  1
#    define MOTOR_COMPILER_NAME "gcc"
#    include <motor/config/compilers/gcc.hh>
#elif defined(__clang__)
#    define MOTOR_COMPILER_CLANG 1
#    define MOTOR_COMPILER_NAME  "clang"
#    include <motor/config/compilers/clang.hh>
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
#define __kernel static inline  // NOLINT(bugprone-reserved-identifier)

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

static_assert(sizeof(u8) == 1, "invalid size for type u8");
static_assert(sizeof(u16) == 2, "invalid size for type u16");
static_assert(sizeof(u32) == 4, "invalid size for type u32");
static_assert(sizeof(u64) == 8, "invalid size for type u64");
static_assert(sizeof(i8) == 1, "invalid size for type i8");
static_assert(sizeof(i16) == 2, "invalid size for type i16");
static_assert(sizeof(i32) == 4, "invalid size for type i32");
static_assert(sizeof(i64) == 8, "invalid size for type i64");

#endif
