/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_FORMAT_H_
#define MOTOR_MINITL_FORMAT_H_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
// #include <motor/minitl/allocator.hh>
#include <motor/kernel/interlocked.hh>
#include <motor/minitl/type_traits.hh>
#include <motor/minitl/utility.hh>
#include <string.h>

namespace minitl {

template < u32 SIZE >
struct format_buffer
{
    char buffer[SIZE];

    operator const char*() const
    {
        return buffer;
    }
    const char* c_str() const
    {
        return buffer;
    }
};

struct format_options
{
    u32  precision;
    u32  width;
    char fill;
    char align;
    char sign;
    char format;
    bool locale;
    bool alternate;
    bool signPadding;
};

template < typename T >
struct formatter;

template < u32 SIZE, typename T, typename... Args >
format_buffer< SIZE > format(const T pattern, Args&&... arguments);

template < u32 SIZE, typename T, typename... Args >
u32 format_to(char* destination, u32 length, const T pattern, Args&&... arguments);

#define FMT(x)                                                                                     \
    []() {                                                                                         \
        struct format_pattern                                                                      \
        {                                                                                          \
            constexpr const char& operator[](unsigned i) const                                     \
            {                                                                                      \
                return x[i];                                                                       \
            }                                                                                      \
            constexpr unsigned size() const                                                        \
            {                                                                                      \
                return sizeof(x);                                                                  \
            }                                                                                      \
        };                                                                                         \
        return format_pattern {};                                                                  \
    }()

}  // namespace minitl

#include <motor/minitl/inl/format.inl>
#include <motor/minitl/inl/formatter.inl>

/**************************************************************************************************/
#endif
