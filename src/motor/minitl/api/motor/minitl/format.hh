/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_FORMAT_HH
#define MOTOR_MINITL_FORMAT_HH

#include <motor/minitl/stdafx.h>
#include <motor/kernel/interlocked.hh>
#include <motor/minitl/allocator.hh>
#include <motor/minitl/utility.hh>
#include <string.h>

namespace minitl {

template < u32 SIZE >
struct format_buffer
{
    char buffer[SIZE];

    operator const char*() const  // NOLINT(google-explicit-constructor)
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
    char formatter;
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

template < u32 SIZE = 1024, typename T, typename... ARGS >
format_buffer< SIZE > format(T format_string, ARGS&&... arguments);

template < typename T, typename... ARGS >
u32 format_to(char* destination, u32 length, T format_string, ARGS&&... arguments);

#define FMT(x)                                                                                     \
    []() {                                                                                         \
        struct format_pattern                                                                      \
        {                                                                                          \
            constexpr const char& operator[](unsigned i) const                                     \
            {                                                                                      \
                return (x)[i];                                                                     \
            }                                                                                      \
            constexpr unsigned size() const                                                        \
            {                                                                                      \
                return sizeof(x);                                                                  \
            }                                                                                      \
        };                                                                                         \
        return format_pattern {};                                                                  \
    }()

}  // namespace minitl

#include <motor/minitl/inl/format.hh>

#endif
