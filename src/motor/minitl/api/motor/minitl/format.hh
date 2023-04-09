/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
// #include <motor/minitl/allocator.hh>
#include <motor/kernel/interlocked.hh>
#include <motor/minitl/type_traits.hh>
#include <motor/minitl/utility.hh>
#include <cstring>

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
    bool locale;
    bool alternate;
    bool signPadding;
};

template < char FORMAT_TYPE >
struct formatter;

/* string-like formatter */
template <>
struct formatter< 's' >;

/* char-like formatter */
template <>
struct formatter< 'c' >;

/* decimal integer formatter */
template <>
struct formatter< 'd' >;

/* binary number formatters */
template <>
struct formatter< 'b' >;
template <>
struct formatter< 'B' >;

/* octal number formatter */
template <>
struct formatter< 'o' >;

/* hexadecimal number formatter */
template <>
struct formatter< 'x' >;
template <>
struct formatter< 'X' >;

/* pointer formatter */
template <>
struct formatter< 'p' >;

/* floating point number formatters */
template <>
struct formatter< 'e' >;
template <>
struct formatter< 'E' >;
template <>
struct formatter< 'f' >;
template <>
struct formatter< 'F' >;
template <>
struct formatter< 'g' >;
template <>
struct formatter< 'G' >;

template < u32 SIZE, typename T, typename... Args >
format_buffer< SIZE > format(T format, Args&&... arguments);

template < u32 SIZE, typename T, typename... Args >
u32 format_to(char* destination, u32 length, T format, Args&&... arguments);

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
