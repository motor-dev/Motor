/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/kernel/interlocked.hh>
#include <cstdio>
#include <cstring>

namespace minitl {

namespace format_details {

struct bool_wrapper
{
    bool_wrapper(bool value) : value(value)  // NOLINT(google-explicit-constructor)
    {
    }

    const bool value;

    operator bool() const  // NOLINT(google-explicit-constructor)
    {
        return value;
    }
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_left_aligned
{
    template < typename T >
    static inline u32 write(char* destination, T value, const format_options& options,
                            u32 reserved_length)
    {
        WRAPPED_FORMATTER::write(destination, value, options, reserved_length);
        if(options.width > reserved_length)
        {
            u32 padding_size = options.width - reserved_length;
            memset(destination + reserved_length, options.fill, padding_size);
            return options.width;
        }
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        if(max_capacity < reserved_length)
        {
            return WRAPPED_FORMATTER::write_partial(destination, value, options, reserved_length,
                                                    max_capacity);
        }
        else
        {
            WRAPPED_FORMATTER::write(destination, value, options, reserved_length);
            u32 padding_size = max_capacity - reserved_length;
            memset(destination + reserved_length, options.fill, padding_size);
            return max_capacity;
        }
    }
    using WRAPPED_FORMATTER::format_length;
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_right_aligned
{
    template < typename T >
    static inline u32 write(char* destination, T value, const format_options& options,
                            u32 reserved_length)
    {
        u32 padding_size = options.width - reserved_length;
        memset(destination, options.fill, padding_size);
        WRAPPED_FORMATTER::wrtie(destination + padding_size, value, options, reserved_length);
        return options.width;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        if(options.width < reserved_length)
        {
            return WRAPPED_FORMATTER::write_partial(destination, value, options, reserved_length,
                                                    max_capacity);
        }
        else
        {
            u32 padding_size = options.width - reserved_length;
            if(padding_size <= max_capacity)
            {
                memset(destination, options.fill, max_capacity);
            }
            else
            {
                memset(destination, options.fill, padding_size);
                WRAPPED_FORMATTER::write_partial(destination + padding_size, value, options,
                                                 max_capacity - padding_size);
            }
            return max_capacity;
        }
    }
    using WRAPPED_FORMATTER::format_length;
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_centered
{
    template < typename T >
    static inline u32 write(char* destination, T value, const format_options& options,
                            u32 reserved_length)
    {
        u32 padding_size      = (options.width - reserved_length);
        u32 padding_size_left = padding_size / 2;
        memset(destination, options.fill, padding_size_left);
        WRAPPED_FORMATTER::format_to(destination + padding_size_left, value, options,
                                     reserved_length);
        memset(destination + padding_size_left + reserved_length, options.fill,
               padding_size - padding_size_left);
        return options.width;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        if(options.width < reserved_length)
        {
            return WRAPPED_FORMATTER::write_partial(destination, value, options, reserved_length,
                                                    max_capacity);
        }
        else
        {
            u32 padding_size      = (options.width - reserved_length);
            u32 padding_size_left = padding_size / 2;
            if(padding_size_left <= max_capacity)
            {
                memset(destination, options.fill, max_capacity);
            }
            else
            {
                memset(destination, options.fill, padding_size_left);
                if(reserved_length + padding_size_left < max_capacity)
                {
                    WRAPPED_FORMATTER::write_partial(destination + padding_size_left, value,
                                                     options, max_capacity - padding_size_left);
                }
                else
                {
                    WRAPPED_FORMATTER::write(destination + padding_size_left, value, options,
                                             reserved_length);
                    memset(destination + padding_size_left + reserved_length, options.fill,
                           max_capacity - padding_size_left - reserved_length);
                }
            }
            return max_capacity;
        }
    }
    using WRAPPED_FORMATTER::format_length;
};

template < typename T >
u32 format_arg_partial_delegate(char* destination, T&& value, const format_options& options,
                                u32 reserved_length, u32 max_capacity)
{
    char* buffer = static_cast< char* >(malloca(reserved_length));
    format_arg(destination, minitl::forward< T >(value), options, reserved_length);
    memcpy(destination, buffer, max_capacity);
    freea(buffer);
    return max_capacity;
}

namespace string_format {

static inline u32 format_length(const char* value, const format_options& options)
{
    motor_forceuse(options);
    return u32(strlen(value));
}

static inline u32 format_arg(char* destination, const char* value, const format_options& options,
                             u32 reserved_length)
{
    motor_forceuse(options);
    memcpy(destination, value, reserved_length);
    return reserved_length;
}

static inline u32 format_arg_partial(char* destination, const char* value,
                                     const format_options& options, u32 reserved_length,
                                     u32 max_capacity)
{
    motor_forceuse(options);
    motor_forceuse(reserved_length);
    memcpy(destination, value, max_capacity);
    return max_capacity;
}

static inline u32 format_length(bool_wrapper value, const format_options& options)
{
    motor_forceuse(options);
    return 5 - u32(value);
}

motor_api(MINITL) u32 format_arg(char* destination, bool_wrapper value,
                                 const format_options& options, u32 reserved_length);
motor_api(MINITL) u32
    format_arg_partial(char* destination, bool_wrapper value, const format_options& options,
                       u32 reserved_length, u32 max_capacity);

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
                            u32 reserved_length)
    {
        using namespace format_details::string_format;
        return format_arg(destination, minitl::forward< T >(value), options, reserved_length);
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        using namespace format_details::string_format;
        return format_arg_partial(destination, minitl::forward< T >(value), options,
                                  reserved_length, max_capacity);
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
                            u32 reserved_length)
    {
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        *destination = value;
        return 1;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        motor_forceuse(max_capacity);
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
                            u32 reserved_length)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        motor_forceuse(max_capacity);
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
                            u32 reserved_length)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        motor_forceuse(max_capacity);
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
                            u32 reserved_length)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        motor_forceuse(max_capacity);
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
                            u32 reserved_length)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        return 0;
    }
    template < typename T >
    static inline u32 write_partial(char* destination, T&& value, const format_options& options,
                                    u32 reserved_length, u32 max_capacity)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        motor_forceuse(max_capacity);
        return 0;
    }
};

}  // namespace minitl
