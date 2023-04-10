/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/kernel/interlocked.hh>
#include <motor/minitl/format.hh>
#include <cstdio>
#include <cstring>

namespace minitl {

namespace format_details {

struct bool_wrapper
{
    bool_wrapper(bool value) : value(value)
    {
    }

    const bool value;

    operator bool() const
    {
        return value;
    }
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_left_aligned
{
    template < typename T >
    static inline u32 write(char* destination, T value, const format_options& options,
                            u32 reservedLength)
    {
        WRAPPED_FORMATTER::write(destination, value, options, reservedLength);
        if(options.width > reservedLength)
        {
            u32 paddingSize = options.width - reservedLength;
            memset(destination + reservedLength, options.fill, paddingSize);
            return options.width;
        }
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        if(maxCapacity < reservedLength)
        {
            return WRAPPED_FORMATTER::write_partial(destination, value, options, reservedLength,
                                                    maxCapacity);
        }
        else
        {
            WRAPPED_FORMATTER::write(destination, value, options, reservedLength);
            u32 paddingSize = maxCapacity - reservedLength;
            memset(destination + reservedLength, options.fill, paddingSize);
            return maxCapacity;
        }
    }
    using WRAPPED_FORMATTER::format_length;
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_right_aligned
{
    template < typename T >
    static inline u32 write(char* destination, T value, const format_options& options,
                            u32 reservedLength)
    {
        u32 paddingSize = options.width - reservedLength;
        memset(destination, options.fill, paddingSize);
        WRAPPED_FORMATTER::wrtie(destination + paddingSize, value, options, reservedLength);
        return options.width;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        if(options.width < reservedLength)
        {
            return WRAPPED_FORMATTER::write_partial(destination, value, options, reservedLength,
                                                    maxCapacity);
        }
        else
        {
            u32 paddingSize = options.width - reservedLength;
            if(paddingSize <= maxCapacity)
            {
                memset(destination, options.fill, maxCapacity);
            }
            else
            {
                memset(destination, options.fill, paddingSize);
                WRAPPED_FORMATTER::write_partial(destination + paddingSize, value, options,
                                                 maxCapacity - paddingSize);
            }
            return maxCapacity;
        }
    }
    using WRAPPED_FORMATTER::format_length;
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_centered
{
    template < typename T >
    static inline u32 write(char* destination, T value, const format_options& options,
                            u32 reservedLength)
    {
        u32 paddingSize     = (options.width - reservedLength);
        u32 paddingSizeLeft = paddingSize / 2;
        memset(destination, options.fill, paddingSizeLeft);
        WRAPPED_FORMATTER::format_to(destination + paddingSizeLeft, value, options, reservedLength);
        memset(destination + paddingSizeLeft + reservedLength, options.fill,
               paddingSize - paddingSizeLeft);
        return options.width;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        if(options.width < reservedLength)
        {
            return WRAPPED_FORMATTER::write_partial(destination, value, options, reservedLength,
                                                    maxCapacity);
        }
        else
        {
            u32 paddingSize     = (options.width - reservedLength);
            u32 paddingSizeLeft = paddingSize / 2;
            if(paddingSizeLeft <= maxCapacity)
            {
                memset(destination, options.fill, maxCapacity);
            }
            else
            {
                memset(destination, options.fill, paddingSizeLeft);
                if(reservedLength + paddingSizeLeft < maxCapacity)
                {
                    WRAPPED_FORMATTER::write_partial(destination + paddingSizeLeft, value, options,
                                                     maxCapacity - paddingSizeLeft);
                }
                else
                {
                    WRAPPED_FORMATTER::write(destination + paddingSizeLeft, value, options,
                                             reservedLength);
                    memset(destination + paddingSizeLeft + reservedLength, options.fill,
                           maxCapacity - paddingSizeLeft - reservedLength);
                }
            }
            return maxCapacity;
        }
    }
    using WRAPPED_FORMATTER::format_length;
};

template < typename T >
u32 format_arg_partial_delegate(char* destination, T&& value, const format_options& options,
                                u32 reservedLength, u32 maxCapacity)
{
    char* buffer = static_cast< char* >(malloca(reservedLength));
    format_arg(destination, minitl::forward< T >(value), options, reservedLength);
    memcpy(destination, buffer, maxCapacity);
    freea(buffer);
    return maxCapacity;
}

namespace string_format {

static inline u32 format_length(const char* value, const format_options& options)
{
    motor_forceuse(options);
    return u32(strlen(value));
}

static inline u32 format_arg(char* destination, const char* value, const format_options& options,
                             u32 reservedLength)
{
    motor_forceuse(options);
    memcpy(destination, value, reservedLength);
    return reservedLength;
}

static inline u32 format_arg_partial(char* destination, const char* value,
                                     const format_options& options, u32 reservedLength,
                                     u32 maxCapacity)
{
    motor_forceuse(options);
    motor_forceuse(reservedLength);
    memcpy(destination, value, maxCapacity);
    return maxCapacity;
}

static inline u32 format_length(bool_wrapper value, const format_options& options)
{
    motor_forceuse(options);
    return 5 - u32(value);
}

motor_api(MINITL) u32 format_arg(char* destination, bool_wrapper value,
                                 const format_options& options, u32 reservedLength);
motor_api(MINITL) u32
    format_arg_partial(char* destination, bool_wrapper value, const format_options& options,
                       u32 reservedLength, u32 maxCapacity);

}  // namespace string_format

}  // namespace format_details

template <>
struct formatter< '{' >
{
    static constexpr format_options default_format_options {0,     0,     ' ',   '<', '-',
                                                            false, false, false, '{'};
};

template <>
struct formatter< 's' >
{
    static constexpr format_options default_format_options {0,     0,     ' ',   '<', '-',
                                                            false, false, false, 's'};
    typedef formatter< 's' >        formatter_alternate;
    typedef format_details::direct_formatter_left_aligned< formatter< 's' > >
        formatter_left_aligned;
    typedef format_details::direct_formatter_right_aligned< formatter< 's' > >
                                                                          formatter_right_aligned;
    typedef format_details::direct_formatter_centered< formatter< 's' > > formatter_centered;

    template < typename T >
    static inline u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::string_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static inline u32 write(char* destination, T&& value, const format_options& options,
                            u32 reservedLength)
    {
        using namespace format_details::string_format;
        return format_arg(destination, minitl::forward< T >(value), options, reservedLength);
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        using namespace format_details::string_format;
        return format_arg_partial(destination, minitl::forward< T >(value), options, reservedLength,
                                  maxCapacity);
    }
};

template <>
struct formatter< 'c' >
{
    static constexpr format_options default_format_options {0,     0,     ' ',   '<', '-',
                                                            false, false, false, 'c'};
    typedef formatter< 'c' >        formatter_alternate;
    typedef format_details::direct_formatter_left_aligned< formatter< 'c' > >
        formatter_left_aligned;
    typedef format_details::direct_formatter_right_aligned< formatter< 'c' > >
                                                                          formatter_right_aligned;
    typedef format_details::direct_formatter_centered< formatter< 'c' > > formatter_centered;

    static inline u32 length(char value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 1;
    }
    static inline u32 write(char* destination, char value, const format_options& options,
                            u32 reservedLength)
    {
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        *destination = value;
        return 1;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        motor_forceuse(maxCapacity);
        return 0;
    }
};

template <>
struct formatter< 'd' >
{
    static constexpr format_options default_format_options {0,     0,     ' ',   '<', '-',
                                                            false, false, false, 'd'};
    typedef formatter< 'g' >        formatter_alternate;
    typedef format_details::direct_formatter_left_aligned< formatter< 'd' > >
        formatter_left_aligned;
    typedef format_details::direct_formatter_right_aligned< formatter< 'd' > >
                                                                          formatter_right_aligned;
    typedef format_details::direct_formatter_centered< formatter< 'd' > > formatter_centered;

    template < typename T >
    static inline u32 length(T&& value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 0;
    }
    template < typename T >
    static inline u32 write(char* destination, T&& value, const format_options& options,
                            u32 reservedLength)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        motor_forceuse(maxCapacity);
        return 0;
    }
};

template <>
struct formatter< 'x' >
{
    static constexpr format_options default_format_options {0,     0,     ' ',   '<', '-',
                                                            false, false, false, 'x'};
    typedef formatter< 'g' >        formatter_alternate;
    typedef format_details::direct_formatter_left_aligned< formatter< 'd' > >
        formatter_left_aligned;
    typedef format_details::direct_formatter_right_aligned< formatter< 'd' > >
                                                                          formatter_right_aligned;
    typedef format_details::direct_formatter_centered< formatter< 'd' > > formatter_centered;

    template < typename T >
    static inline u32 length(T&& value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 0;
    }
    template < typename T >
    static inline u32 write(char* destination, T&& value, const format_options& options,
                            u32 reservedLength)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        motor_forceuse(maxCapacity);
        return 0;
    }
};

template <>
struct formatter< 'p' >
{
    static constexpr format_options default_format_options {0,     0,     ' ',   '<', '-',
                                                            false, false, false, 'p'};
    typedef formatter< 'g' >        formatter_alternate;
    typedef format_details::direct_formatter_left_aligned< formatter< 'p' > >
        formatter_left_aligned;
    typedef format_details::direct_formatter_right_aligned< formatter< 'p' > >
                                                                          formatter_right_aligned;
    typedef format_details::direct_formatter_centered< formatter< 'p' > > formatter_centered;

    template < typename T >
    static inline u32 length(T&& value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 0;
    }
    template < typename T >
    static inline u32 write(char* destination, T&& value, const format_options& options,
                            u32 reservedLength)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        motor_forceuse(maxCapacity);
        return 0;
    }
};

template <>
struct formatter< 'g' >
{
    static constexpr format_options default_format_options {0,     0,     ' ',   '<', '-',
                                                            false, false, false, 'g'};
    typedef formatter< 'g' >        formatter_alternate;
    typedef format_details::direct_formatter_left_aligned< formatter< 'g' > >
        formatter_left_aligned;
    typedef format_details::direct_formatter_right_aligned< formatter< 'g' > >
                                                                          formatter_right_aligned;
    typedef format_details::direct_formatter_centered< formatter< 'g' > > formatter_centered;

    template < typename T >
    static inline u32 length(T&& value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 0;
    }
    template < typename T >
    static inline u32 write(char* destination, T&& value, const format_options& options,
                            u32 reservedLength)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reservedLength, u32 maxCapacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        motor_forceuse(maxCapacity);
        return 0;
    }
};

}  // namespace minitl
