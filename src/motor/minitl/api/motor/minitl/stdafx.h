/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_STDAFX_HH
#define MOTOR_MINITL_STDAFX_HH

#include <motor/kernel/stdafx.h>

#if defined(MOTOR_COMPUTE)
#    define motor_api(module)
#else
// NOLINTNEXTLINE(readability-identifier-naming)
#    define motor_api(module) MOTOR_API_##module
#endif

#if defined(building_minitl)
#    define MOTOR_API_MINITL MOTOR_EXPORT
#elif defined(motor_dll_minitl)
#    define MOTOR_API_MINITL MOTOR_IMPORT
#else
#    define MOTOR_API_MINITL
#endif

#include <motor/kernel/interlocked.hh>
#include <motor/kernel/simd.hh>
#include <motor/minitl/features.hh>

namespace minitl {

template < typename T >
inline T align(T value, size_t alignment)
{
    auto v = (size_t)(value);
    return (T)(alignment == v ? v : ((v + alignment - 1) & ~(alignment - 1)));
}

template < typename T >
T min(T t1, T t2)
{
    return t1 < t2 ? t1 : t2;
}

template < typename T >
T max(T t1, T t2)
{
    return t1 > t2 ? t1 : t2;
}

template < typename T >
inline T next_power_of_2(T t)
{
    u64 result = t;
    result -= 1;
    result |= result >> 1;
    result |= result >> 2;
    result |= result >> 4;
    result |= result >> 8;
    result |= result >> 16;
    result |= result >> 32;
    return static_cast< T >(result + 1);
}

/* allows declaring format methods without including format.hh */
struct format_options;

}  // namespace minitl

#endif
