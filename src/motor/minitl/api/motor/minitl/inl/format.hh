/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_FORMAT_HH
#define MOTOR_MINITL_INL_FORMAT_HH

#include <motor/minitl/format.hh>

#include <motor/kernel/interlocked.hh>
#include <motor/minitl/integer_types.hh>
#include <motor/minitl/tuple.hh>
#include <stdio.h>
#include <string.h>

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
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        return WRAPPED_FORMATTER::length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static u32 write(char* destination, T&& value, const format_options& options,
                     u32 reserved_length)
    {
        WRAPPED_FORMATTER::write(destination, minitl::forward< T >(value), options,
                                 reserved_length);
        if(options.width > reserved_length)
        {
            u32 padding_size = options.width - reserved_length;
            memset(destination + reserved_length, options.fill, padding_size);
            return options.width;
        }
        else
        {
            return reserved_length;
        }
    }
    template < typename T >
    static u32 write_partial(char* destination, T&& value, const format_options& options,
                             u32 reserved_length, u32 max_capacity)
    {
        if(reserved_length < max_capacity)
        {
            WRAPPED_FORMATTER::write(destination, minitl::forward< T >(value), options,
                                     reserved_length);
            u32 padding_size = max_capacity - reserved_length;
            memset(destination + reserved_length, options.fill, padding_size);
            return max_capacity;
        }
        else
        {
            return WRAPPED_FORMATTER::write_partial(destination, minitl::forward< T >(value),
                                                    options, reserved_length, max_capacity);
        }
    }
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_right_aligned
{
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        return WRAPPED_FORMATTER::length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static u32 write(char* destination, T&& value, const format_options& options,
                     u32 reserved_length)
    {
        if(options.width > reserved_length)
        {
            u32 padding_size = options.width - reserved_length;
            memset(destination, options.fill, padding_size);
            WRAPPED_FORMATTER::write(destination + padding_size, minitl::forward< T >(value),
                                     options, reserved_length);
            return options.width;
        }
        else
        {
            return WRAPPED_FORMATTER::write(destination, minitl::forward< T >(value), options,
                                            reserved_length);
        }
    }
    template < typename T >
    static u32 write_partial(char* destination, T&& value, const format_options& options,
                             u32 reserved_length, u32 max_capacity)
    {
        if(options.width > reserved_length)
        {
            u32 padding_size = options.width - reserved_length;
            if(padding_size <= max_capacity)
            {
                memset(destination, options.fill, padding_size);
                WRAPPED_FORMATTER::write_partial(destination + padding_size,
                                                 minitl::forward< T >(value), options,
                                                 reserved_length, max_capacity - padding_size);
            }
            else
            {
                memset(destination, options.fill, max_capacity);
            }
            return max_capacity;
        }
        else
        {
            return WRAPPED_FORMATTER::write_partial(destination, minitl::forward< T >(value),
                                                    options, reserved_length, max_capacity);
        }
    }
};

template < typename WRAPPED_FORMATTER >
struct direct_formatter_centered
{
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        return WRAPPED_FORMATTER::length(minitl::forward< T >(minitl::forward< T >(value)),
                                         options);
    }
    template < typename T >
    static u32 write(char* destination, T&& value, const format_options& options,
                     u32 reserved_length)
    {
        if(options.width > reserved_length)
        {
            u32 padding_size      = (options.width - reserved_length);
            u32 padding_size_left = padding_size / 2;
            memset(destination, options.fill, padding_size_left);
            WRAPPED_FORMATTER::write(destination + padding_size_left, minitl::forward< T >(value),
                                     options, reserved_length);
            memset(destination + padding_size_left + reserved_length, options.fill,
                   padding_size - padding_size_left);
            return options.width;
        }
        else
        {
            return WRAPPED_FORMATTER::write(destination, minitl::forward< T >(value), options,
                                            reserved_length);
        }
    }
    template < typename T >
    static u32 write_partial(char* destination, T&& value, const format_options& options,
                             u32 reserved_length, u32 max_capacity)
    {
        if(options.width < reserved_length)
        {
            return WRAPPED_FORMATTER::write_partial(destination, minitl::forward< T >(value),
                                                    options, reserved_length, max_capacity);
        }
        else
        {
            u32 padding_size      = (options.width - reserved_length);
            u32 padding_size_left = padding_size / 2;
            if(padding_size_left <= max_capacity)
            {
                memset(destination, options.fill, padding_size_left);
                if(reserved_length + padding_size_left < max_capacity)
                {
                    WRAPPED_FORMATTER::write(destination + padding_size_left,
                                             minitl::forward< T >(value), options, reserved_length);
                    memset(destination + padding_size_left + reserved_length, options.fill,
                           max_capacity - padding_size_left - reserved_length);
                }
                else
                {
                    WRAPPED_FORMATTER::write_partial(
                        destination + padding_size_left, minitl::forward< T >(value), options,
                        reserved_length, max_capacity - padding_size_left);
                }
            }
            else
            {
                memset(destination, options.fill, max_capacity);
            }
            return max_capacity;
        }
    }
};

template < typename WRAPPED_FORMATTER >
struct buffered_formatter_left_aligned
{
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        return WRAPPED_FORMATTER::length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static u32 write(char* destination, T&& value, const format_options& options,
                     u32 reserved_length)
    {
        reserved_length = WRAPPED_FORMATTER::write(destination, minitl::forward< T >(value),
                                                   options, reserved_length);
        if(options.width > reserved_length)
        {
            u32 padding_size = options.width - reserved_length;
            memset(destination + reserved_length, options.fill, padding_size);
            return options.width;
        }
        else
        {
            return reserved_length;
        }
    }
    template < typename T >
    static u32 write_partial(char* destination, T&& value, const format_options& options,
                             u32 reserved_length, u32 max_capacity)
    {
        reserved_length = WRAPPED_FORMATTER::write_partial(destination, minitl::forward< T >(value),
                                                           options, reserved_length, max_capacity);
        if(max_capacity > reserved_length)
        {
            u32 padding_size = max_capacity - reserved_length;
            memset(destination + reserved_length, options.fill, padding_size);
            return max_capacity;
        }
        else
        {
            return reserved_length;
        }
    }
};

template < typename WRAPPED_FORMATTER >
struct buffered_formatter_right_aligned
{
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        return WRAPPED_FORMATTER::length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static u32 write(char* destination, T&& value, const format_options& options,
                     u32 reserved_length)
    {
        char* buffer    = static_cast< char* >(malloca(reserved_length));
        reserved_length = WRAPPED_FORMATTER::write(buffer, minitl::forward< T >(value), options,
                                                   reserved_length);
        u32 result      = reserved_length;
        if(options.width > reserved_length)
        {
            u32 padding_size = options.width - reserved_length;
            memset(destination, options.fill, padding_size);
            destination += padding_size;
            result += padding_size;
        }
        memcpy(destination, buffer, reserved_length);
        freea(buffer);
        return result;
    }

    template < typename T >
    static u32 write_partial(char* destination, T value, const format_options& options,
                             u32 reserved_length, u32 max_capacity)
    {
        char* buffer    = static_cast< char* >(malloca(reserved_length));
        reserved_length = WRAPPED_FORMATTER::write(buffer, minitl::forward< T >(value), options,
                                                   reserved_length);
        u32 result      = 0;
        if(options.width > reserved_length)
        {
            u32 padding_size = options.width - reserved_length;
            if(padding_size < max_capacity)
            {
                memset(destination, options.fill, padding_size);
                result += padding_size;
                max_capacity -= padding_size;
                reserved_length = reserved_length > max_capacity ? max_capacity : reserved_length;
                memcpy(destination + padding_size, buffer, reserved_length);
                result += reserved_length;
            }
            else
            {
                memset(destination, options.fill, max_capacity);
                result += max_capacity;
            }
        }
        else
        {
            reserved_length = reserved_length > max_capacity ? max_capacity : reserved_length;
            memcpy(destination, buffer, reserved_length);
            result += reserved_length;
        }
        freea(buffer);
        return result;
    }
};

template < typename WRAPPED_FORMATTER >
struct buffered_formatter_centered
{
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        return WRAPPED_FORMATTER::length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static u32 write(char* destination, T value, const format_options& options, u32 reserved_length)
    {
        char* buffer    = static_cast< char* >(malloca(reserved_length));
        reserved_length = WRAPPED_FORMATTER::write(buffer, minitl::forward< T >(value), options,
                                                   reserved_length);
        u32 result      = reserved_length;
        if(reserved_length < options.width)
        {
            u32 padding_size = (options.width - reserved_length);
            result += padding_size;
            u32 padding_size_left = padding_size / 2;
            memset(destination, options.fill, padding_size_left);
            memcpy(destination + padding_size_left, buffer, reserved_length);
            memset(destination + padding_size_left + reserved_length, options.fill,
                   padding_size - padding_size_left);
        }
        else
        {
            memcpy(destination, buffer, reserved_length);
        }
        freea(buffer);
        return result;
    }
    template < typename T >
    static u32 write_partial(char* destination, T value, const format_options& options,
                             u32 reserved_length, u32 max_capacity)
    {
        char* buffer    = static_cast< char* >(malloca(reserved_length));
        reserved_length = WRAPPED_FORMATTER::write(buffer, minitl::forward< T >(value), options,
                                                   reserved_length);
        u32 result      = 0;
        if(reserved_length < options.width)
        {
            u32 padding_size      = (options.width - reserved_length);
            u32 padding_size_left = padding_size / 2;
            if(padding_size_left <= max_capacity)
            {
                memset(destination, options.fill, padding_size_left);
                max_capacity -= padding_size_left;

                if(reserved_length < max_capacity)
                {
                    memcpy(destination + padding_size_left, buffer, reserved_length);
                    if(options.width < max_capacity)
                    {
                        result += reserved_length + padding_size;
                        memset(destination + padding_size_left + reserved_length, options.fill,
                               padding_size - padding_size_left);
                    }
                    else
                    {
                        result += max_capacity + padding_size_left;
                        memset(destination + padding_size_left + reserved_length, options.fill,
                               max_capacity - reserved_length);
                    }
                }
                else
                {
                    memcpy(destination + padding_size_left, buffer, max_capacity);
                    result += max_capacity + padding_size_left;
                }
            }
            else
            {
                memset(destination, options.fill, max_capacity);
                result += max_capacity;
            }
        }
        else
        {
            result += (reserved_length > max_capacity) ? max_capacity : reserved_length;
            memcpy(destination, buffer, result);
        }
        freea(buffer);
        return result;
    }
};

template < typename WRAPPED_FORMATTER >
struct buffered_formatter_sign_aware
{
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        return WRAPPED_FORMATTER::length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static u32 write(char* destination, T value, const format_options& options, u32 reserved_length)
    {
        char* buffer    = static_cast< char* >(malloca(reserved_length));
        reserved_length = WRAPPED_FORMATTER::write(buffer, minitl::forward< T >(value), options,
                                                   reserved_length);
        u32 prefix      = (value < 0) | (options.sign == '+');
        prefix += options.alternate * WRAPPED_FORMATTER::prefix_length;
        u32 result = reserved_length;
        if(reserved_length < options.width)
        {
            u32 padding_size = (options.width - reserved_length);
            result += padding_size;
            memcpy(destination, buffer, prefix);
            reserved_length -= prefix;
            memset(destination + prefix, options.fill, padding_size);
            memcpy(destination + prefix + padding_size, buffer + prefix, reserved_length);
        }
        else
        {
            memcpy(destination, buffer, reserved_length);
        }
        freea(buffer);
        return result;
    }
    template < typename T >
    static u32 write_partial(char* destination, T value, const format_options& options,
                             u32 reserved_length, u32 max_capacity)
    {
        char* buffer    = static_cast< char* >(malloca(reserved_length));
        reserved_length = WRAPPED_FORMATTER::write(buffer, minitl::forward< T >(value), options,
                                                   reserved_length);
        u32 prefix      = (value < 0) | (options.sign == '+');
        prefix += options.alternate * WRAPPED_FORMATTER::prefix_length;
        u32 result = 0;
        if(reserved_length < options.width)
        {
            if(prefix < max_capacity)
            {
                result += prefix;
                max_capacity -= prefix;
                reserved_length -= prefix;
                memcpy(destination, buffer, prefix);
                u32 padding_size = (options.width - reserved_length);
                if(padding_size < max_capacity)
                {
                    result += padding_size;
                    memset(destination + prefix, options.fill, padding_size);
                    max_capacity -= padding_size;

                    if(reserved_length < max_capacity)
                    {
                        result += reserved_length;
                        memcpy(destination + prefix + padding_size, buffer, reserved_length);
                    }
                    else
                    {
                        memcpy(destination + prefix + padding_size, buffer, max_capacity);
                        result += max_capacity;
                    }
                }
                else
                {
                    memset(destination + prefix, options.fill, max_capacity);
                    result += max_capacity;
                }
            }
            else
            {
                result += max_capacity;
                memcpy(destination, buffer, max_capacity);
            }
        }
        else
        {
            result += (reserved_length > max_capacity) ? max_capacity : reserved_length;
            memcpy(destination, buffer, result);
        }
        freea(buffer);
        return result;
    }
};

template < typename T, typename WRAPPED_FORMATTER >
static MOTOR_ALWAYS_INLINE u32 format_arg_partial_delegate(char* destination, T&& value,
                                                           const format_options& options,
                                                           u32 reserved_length, u32 max_capacity)
{
    char* buffer = static_cast< char* >(malloca(reserved_length));
    WRAPPED_FORMATTER::write(buffer, minitl::forward< T >(value), options, reserved_length);
    memcpy(destination, buffer, max_capacity);
    freea(buffer);
    return max_capacity;
}

template < typename WRAPPED_FORMATTER >
struct direct_aligned_formatter
{
    typedef format_details::direct_formatter_left_aligned< WRAPPED_FORMATTER >
        formatter_left_aligned_t;
    typedef format_details::direct_formatter_right_aligned< WRAPPED_FORMATTER >
        formatter_right_aligned_t;
    typedef format_details::direct_formatter_centered< WRAPPED_FORMATTER > formatter_centered_t;
    typedef format_details::direct_formatter_right_aligned< WRAPPED_FORMATTER >
        formatter_sign_aware_t;
};

template < typename WRAPPED_FORMATTER >
struct buffered_partial_formatter
{
    typedef format_details::buffered_formatter_left_aligned< WRAPPED_FORMATTER >
        formatter_left_aligned_t;
    typedef format_details::buffered_formatter_right_aligned< WRAPPED_FORMATTER >
        formatter_right_aligned_t;
    typedef format_details::buffered_formatter_centered< WRAPPED_FORMATTER > formatter_centered_t;
    typedef format_details::buffered_formatter_sign_aware< WRAPPED_FORMATTER >
        formatter_sign_aware_t;
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write_partial(char* destination, T&& value,
                                                 const format_options& options, u32 reserved_length,
                                                 u32 max_capacity)
    {
        return format_arg_partial_delegate< T, WRAPPED_FORMATTER >(
            destination, minitl::forward< T >(value), options, reserved_length, max_capacity);
    }
};

template < char FORMAT >
struct numeric_formatter : public buffered_partial_formatter< formatter< FORMAT > >
{
    static constexpr format_options default_format_options {0,   0,     ' ',   '>',
                                                            '-', false, false, FORMAT};
};

namespace decimal_format {

template < typename T >
static MOTOR_ALWAYS_INLINE u32 format_length(T value, const format_options& options)
{
    motor_forceuse(value);
    motor_forceuse(options);
    // 1 -> 3
    // 2 -> 5
    // 4 -> 11
    // 8 -> 20 / actually 21
    return 1 + (sizeof(T) * 2) + 2 * (sizeof(T) / 4) + 1;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long long number, const format_options& options);

}  // namespace decimal_format

namespace hexadecimal_format {

template < typename T >
static MOTOR_ALWAYS_INLINE u32 format_length(T value, const format_options& options)
{
    motor_forceuse(value);
    return (sizeof(T) * 2) + 1 + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long long number, const format_options& options);

motor_api(MINITL) u32 format_hexadecimal_whole(char* destination, u32 number);
motor_api(MINITL) u32 format_hexadecimal_whole(char* destination, u64 number);

}  // namespace hexadecimal_format

namespace binary_format {

template < typename T >
static MOTOR_ALWAYS_INLINE u32 format_length(T value, const format_options& options)
{
    motor_forceuse(value);
    return (sizeof(T) * 8) + 1 + 2 * options.alternate;
}

template < u32 SIZE, bool IS_SIGNED >
u32 format_arg_size(char* destination, signed_integer_type_t< SIZE > number,
                    const format_options& options);
template < u32 SIZE, bool IS_SIGNED >
u32 format_arg_size(char* destination, unsigned_integer_type_t< SIZE > number,
                    const format_options& options);

motor_api(MINITL) u32
    format_arg(char* destination, signed char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long long number, const format_options& options);

}  // namespace binary_format

namespace octal_format {

template < typename T >
static MOTOR_ALWAYS_INLINE u32 format_length(T value, const format_options& options)
{
    motor_forceuse(value);
    return (sizeof(T) * 8 + 2) / 3 + 1 + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, signed long long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned char number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned short number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned int number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long number, const format_options& options);
motor_api(MINITL) u32
    format_arg(char* destination, unsigned long long number, const format_options& options);

}  // namespace octal_format

namespace pointer_format {

static MOTOR_ALWAYS_INLINE u32 format_length(const void* value, const format_options& options)
{
    motor_forceuse(value);
    return sizeof(const void*) * 2 + options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, const void* value, const format_options& options);

}  // namespace pointer_format

namespace string_format {

static MOTOR_ALWAYS_INLINE u32 format_length(const char* value, const format_options& options)
{
    motor_forceuse(options);
    return u32(strlen(value));
}

static MOTOR_ALWAYS_INLINE u32 format_arg(char* destination, const char* value,
                                          const format_options& options, u32 reserved_length)
{
    motor_forceuse(options);
    memcpy(destination, value, reserved_length);
    return reserved_length;
}

static MOTOR_ALWAYS_INLINE u32 format_arg_partial(char* destination, const char* value,
                                                  const format_options& options,
                                                  u32 reserved_length, u32 max_capacity)
{
    motor_forceuse(options);
    motor_forceuse(reserved_length);
    memcpy(destination, value, max_capacity);
    return max_capacity;
}

static MOTOR_ALWAYS_INLINE u32 format_length(bool_wrapper value, const format_options& options)
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
    static constexpr format_options default_format_options {0, 0, ' ', '<', '-', false, false, '{'};
};

template <>
struct formatter< 's' > : format_details::direct_aligned_formatter< formatter< 's' > >
{
    static constexpr format_options default_format_options {0, 0, ' ', '<', '-', false, false, 's'};

    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::string_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        using namespace format_details::string_format;
        return format_arg(destination, minitl::forward< T >(value), options, reserved_length);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write_partial(char* destination, T&& value,
                                                 const format_options& options, u32 reserved_length,
                                                 u32 max_capacity)
    {
        using namespace format_details::string_format;
        return format_arg_partial(destination, minitl::forward< T >(value), options,
                                  reserved_length, max_capacity);
    }
};

template <>
struct formatter< 'c' > : format_details::buffered_partial_formatter< formatter< 'c' > >
{
    static constexpr format_options default_format_options {0, 0, ' ', '<', '-', false, false, 'c'};
    static MOTOR_ALWAYS_INLINE u32  length(char value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 1;
    }
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, char value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        *destination = value;
        return 1;
    }
};

template <>
struct formatter< 'd' > : format_details::numeric_formatter< 'd' >
{
    static constexpr u32 prefix_length = 0;
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::decimal_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        using namespace format_details::decimal_format;
        motor_forceuse(reserved_length);
        return format_arg(destination, minitl::forward< T >(value), options);
    }
};

template <>
struct formatter< 'o' > : format_details::numeric_formatter< 'o' >
{
    static constexpr u32 prefix_length = 1;
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::octal_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(reserved_length);
        using namespace format_details::octal_format;
        return format_arg(destination, minitl::forward< T >(value), options);
    }
};

template <>
struct formatter< 'x' > : format_details::numeric_formatter< 'x' >
{
    static constexpr u32 prefix_length = 2;
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::hexadecimal_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(reserved_length);
        using namespace format_details::hexadecimal_format;
        return format_arg(destination, minitl::forward< T >(value), options);
    }
};

template <>
struct formatter< 'X' > : format_details::numeric_formatter< 'X' >
{
    static constexpr u32 prefix_length = 2;
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::hexadecimal_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(reserved_length);
        using namespace format_details::hexadecimal_format;
        return format_arg(destination, minitl::forward< T >(value), options);
    }
};

template <>
struct formatter< 'b' > : format_details::numeric_formatter< 'b' >
{
    static constexpr u32 prefix_length = 2;
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::binary_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(reserved_length);
        using namespace format_details::binary_format;
        return format_arg(destination, minitl::forward< T >(value), options);
    }
};

template <>
struct formatter< 'B' > : format_details::numeric_formatter< 'B' >
{
    static constexpr u32 prefix_length = 2;
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::binary_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(reserved_length);
        using namespace format_details::binary_format;
        return format_arg(destination, minitl::forward< T >(value), options);
    }
};

template <>
struct formatter< 'p' > : format_details::buffered_partial_formatter< formatter< 'p' > >
{
    static constexpr format_options default_format_options {0, 0, ' ', '<', '-', false, false, 'p'};
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        using namespace format_details::pointer_format;
        return format_length(minitl::forward< T >(value), options);
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(reserved_length);
        using namespace format_details::pointer_format;
        return format_arg(destination, minitl::forward< T >(value), options);
    }
};

template <>
struct formatter< 'g' > : format_details::buffered_partial_formatter< formatter< 'g' > >
{
    static constexpr format_options default_format_options {0, 0, ' ', '<', '-', false, false, 'g'};
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 length(T&& value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 0;
    }
    template < typename T >
    static MOTOR_ALWAYS_INLINE u32 write(char* destination, T&& value,
                                         const format_options& options, u32 reserved_length)
    {
        motor_forceuse(destination);
        motor_forceuse(value);
        motor_forceuse(options);
        motor_forceuse(reserved_length);
        return 0;
    }
};

namespace format_details {

/* default is to use the String formatter. */
formatter< 's' > format_as(...);

formatter< 's' > format_as(const char*);
formatter< 's' > format_as(format_details::bool_wrapper);
formatter< 'c' > format_as(char);
formatter< 'd' > format_as(int);
formatter< 'd' > format_as(unsigned int);
formatter< 'd' > format_as(long int);
formatter< 'd' > format_as(unsigned long int);
formatter< 'd' > format_as(long long int);
formatter< 'd' > format_as(unsigned long long int);
formatter< 'p' > format_as(const void*);
formatter< 'g' > format_as(double);

motor_api(MINITL) bool invalid_format(const char* reason);

struct format_pattern_info
{
    u32            block_start;
    u32            pattern_start;
    u32            pattern_end;
    u32            argument_index;
    format_options options;
    bool           error;
};

struct brace_format
{
};

struct pattern_range
{
    u32 block_start;
    u32 pattern_start;
};

template < typename T >
constexpr u32 count_patterns(T format)
{
    u32 count = 0;
    for(int i = 0; format[i] != 0; ++i)
    {
        if(format[i] == '{')
        {
            ++count;
            if(format[i + 1] == '{')
            {
                ++i;
            }
            else
            {
                for(; format[i] != '}' && format[i] != 0; ++i)
                    /* nothing */;
            }
        }
        else if(format[i] == '}')
        {
            if(format[i + 1] == '}')
            {
                ++count;
                ++i;
            }
        }
    }
    return count;
}

template < typename T >
constexpr pattern_range get_pattern_start(u32 pattern_index, u32 start_index)
{
    T   format {};
    u32 first  = start_index;
    u32 result = start_index;
    for(; format[result] != 0; ++result)
    {
        if(format[result] == '{')
        {
            if(pattern_index == 0)
            {
                return {first, result};
            }
            ++result;
            pattern_index--;
            if(format[result] == '{')
            {
                first = result + 1;
            }
            else
            {
                for(; format[result] != '}' && format[result] != 0; ++result)
                    /* nothing */;
                first = result + 1;
            }
        }
        else if(format[result] == '}')
        {
            if(format[result + 1] == '}')
            {
                if(pattern_index == 0)
                {
                    return {first, result};
                }
                ++result;
                pattern_index--;
                first = result + 1;
            }
        }
    }
    return {first, result};
}

constexpr void fill_format_info_default_options(char format, format_pattern_info& result)
{
    switch(format)
    {
    case '{': result.options = formatter< '{' >::default_format_options; break;
    case 's': result.options = formatter< 's' >::default_format_options; break;
    case 'c': result.options = formatter< 'c' >::default_format_options; break;
    case 'd': result.options = formatter< 'd' >::default_format_options; break;
    case 'b': result.options = formatter< 'b' >::default_format_options; break;
    case 'B': result.options = formatter< 'B' >::default_format_options; break;
    case 'o': result.options = formatter< 'o' >::default_format_options; break;
    case 'x': result.options = formatter< 'x' >::default_format_options; break;
    case 'X': result.options = formatter< 'X' >::default_format_options; break;
    // case 'e': result.options = formatter< 'e' >::default_format_options; break;
    // case 'E': result.options = formatter< 'E' >::default_format_options; break;
    // case 'f': result.options = formatter< 'f' >::default_format_options; break;
    // case 'F': result.options = formatter< 'F' >::default_format_options; break;
    case 'g': result.options = formatter< 'g' >::default_format_options; break;
    // case 'G': result.options = formatter< 'G' >::default_format_options; break;
    case 'p': result.options = formatter< 'p' >::default_format_options; break;
    default: result.error = invalid_format("unknown format specifier");
    }
}

template < typename T >
constexpr void fill_format_info_formatter(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] != '}')
    {
        fill_format_info_default_options(format[offset], result);
        offset++;
        if(format[offset] != '}')
        {
            result.error = invalid_format("missing '}' in format specifier");
        }
    }
    result.pattern_end = offset + 1;
}

template < typename T >
constexpr void fill_format_info_precision(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] == '.')
    {
        u32 precision = 0;
        offset++;
        for(; format[offset] >= '0' && format[offset] <= '9'; offset++)
            precision = precision * 10 + format[offset] - '0';
        fill_format_info_formatter(format, offset, result);
        result.options.precision = precision;
    }
    else
    {
        fill_format_info_formatter(format, offset, result);
    }
}

template < typename T >
constexpr void fill_format_info_width(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] >= '0' && format[offset] <= '9')
    {
        u32 width = 0;
        for(; format[offset] >= '0' && format[offset] <= '9'; offset++)
            width = width * 10 + format[offset] - '0';
        fill_format_info_precision(format, offset, result);
        result.options.width = width;
    }
    else
    {
        fill_format_info_precision(format, offset, result);
    }
}

template < typename T >
constexpr void fill_format_info_alternate(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] == '#')
    {
        fill_format_info_width(format, offset + 1, result);
        result.options.alternate = true;
    }
    else
    {
        fill_format_info_width(format, offset, result);
    }
}

template < typename T >
constexpr void fill_format_info_sign(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] == ' ' || format[offset] == '-' || format[offset] == '+')
    {
        fill_format_info_alternate(format, offset + 1, result);
        result.options.sign = format[offset];
    }
    else
    {
        fill_format_info_alternate(format, offset, result);
    }
}

template < typename T >
constexpr void fill_format_info_align(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] == '<' || format[offset] == '>' || format[offset] == '^')
    {
        fill_format_info_sign(format, offset + 1, result);
        result.options.align = format[offset];
    }
    else if(format[offset] == '=')
    {
        fill_format_info_sign(format, offset + 1, result);
        result.options.align = format[offset];
        result.options.fill  = '0';
    }
    else if(format[offset + 1] == '<' || format[offset + 1] == '>' || format[offset + 1] == '^')
    {
        fill_format_info_sign(format, offset + 2, result);
        result.options.fill  = format[offset];
        result.options.align = format[offset + 1];
    }
    else
    {
        fill_format_info_sign(format, offset, result);
    }
}

template < typename T, u32 PATTERN_INDEX, typename... DEFAULT_FORMATTERS >
constexpr format_pattern_info get_format_info(T format)
{
    constexpr u32            argument_count = sizeof...(DEFAULT_FORMATTERS);
    constexpr format_options default_format[argument_count]
        = {DEFAULT_FORMATTERS::default_format_options...};
    pattern_range range         = get_pattern_start< T >(PATTERN_INDEX, 0);
    u32           pattern_start = range.pattern_start;

    if(format[pattern_start] == '}')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {range.block_start,
                pattern_start + 1,
                pattern_start + 2,
                argument_count,
                formatter< '{' >::default_format_options,
                format[pattern_start + 1] != '}'
                    && invalid_format("unmatched '}' in format string")};
    }

    if(format[pattern_start + 1] == '{')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {range.block_start,
                pattern_start + 1,
                pattern_start + 2,
                argument_count,
                formatter< '{' >::default_format_options,
                false};
    }

    u32 argument_offset = pattern_start + 1;
    if(format[argument_offset] == '}' || format[argument_offset] == ':')
    {
        return {range.block_start,
                pattern_start,
                pattern_start + 1,
                argument_count,
                formatter< 's' >::default_format_options,
                invalid_format("argument index is empty")};
    }

    u32 argument_index = 0;
    for(; format[argument_offset] != '}' && format[argument_offset] != ':'; ++argument_offset)
    {
        if(format[argument_offset] < '0' || format[argument_offset] > '9')
        {
            return {range.block_start,
                    pattern_start,
                    pattern_start + 1,
                    argument_count,
                    formatter< 's' >::default_format_options,
                    invalid_format("argument index is not a number")};
        }
        argument_index = argument_index * 10 + format[argument_offset] - '0';
    }

    if(argument_index >= argument_count)
    {
        return {range.block_start,
                pattern_start,
                pattern_start + 1,
                argument_count,
                formatter< 's' >::default_format_options,
                invalid_format("argument index out of range")};
    }
    format_pattern_info result = {range.block_start,
                                  pattern_start,
                                  argument_offset + 1,
                                  argument_index,
                                  default_format[argument_index],
                                  false};
    if(format[argument_offset] == ':')
    {
        fill_format_info_align(format, argument_offset + 1, result);
    }
    return result;
}

template < typename T, u32 PATTERN_INDEX >
constexpr format_pattern_info get_format_info_end(T format, u32 block_start)
{
    return {block_start,
            format.size(),
            format.size(),
            PATTERN_INDEX,
            formatter< '{' >::default_format_options,
            false};
}

template < u32 INDEX >
constexpr bool is_index_in_list()
{
    return invalid_format("argument not used in format");
}

template < u32 INDEX, u32 FIRST, u32... INDICES, enable_if_t< INDEX == FIRST, bool > = true >
constexpr bool is_index_in_list()
{
    return true;
}

template < u32 INDEX, u32 FIRST, u32... INDICES, enable_if_t< INDEX != FIRST, int > = true >
constexpr bool is_index_in_list()
{
    return is_index_in_list< INDEX, INDICES... >();
}

template < typename T, typename FORMATTER, typename ARG >
u32 fill_buffer(char* destination, u32 length, u32 offset, const format_pattern_info& pattern_info,
                u32 argument_length, const FORMATTER& formatter, ARG&& arg)
{
    T   format;
    u32 max_size       = length - offset;
    u32 field_width    = argument_length < pattern_info.options.width ? pattern_info.options.width
                                                                      : argument_length;
    u32 segment_length = pattern_info.pattern_start - pattern_info.block_start;
    segment_length     = segment_length > max_size ? max_size : segment_length;
    memcpy(destination + offset, &format[pattern_info.block_start], segment_length);
    offset += segment_length;
    max_size -= segment_length;
    if(field_width <= max_size)
    {
        offset += formatter.write(destination + offset, minitl::forward< ARG >(arg),
                                  pattern_info.options, argument_length);
    }
    else if(max_size > 0)
    {
        offset += formatter.write_partial(destination + offset, minitl::forward< ARG >(arg),
                                          pattern_info.options, argument_length, max_size);
    }
    return offset;
}

template < typename T >
u32 fill_buffer(char* destination, u32 length, u32 offset, const format_pattern_info& pattern_info,
                u32 argument_length, const formatter< '{' >&, const brace_format&)
{
    motor_forceuse(argument_length);
    T   format;
    u32 max_size       = length - offset;
    u32 segment_length = pattern_info.pattern_start - pattern_info.block_start;
    segment_length     = segment_length > max_size ? max_size : segment_length;
    memcpy(destination + offset, &format[pattern_info.block_start], segment_length);
    return offset + segment_length;
}

enum struct format_alignment
{
    none,
    left,
    right,
    center,
    sign_aware
};

template < typename FORMATTER, format_alignment >
struct aligned_formatter;

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::none >
{
    typedef FORMATTER formatter_t;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::left >
{
    typedef typename FORMATTER::formatter_left_aligned_t formatter_t;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::right >
{
    typedef typename FORMATTER::formatter_right_aligned_t formatter_t;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::center >
{
    typedef typename FORMATTER::formatter_centered_t formatter_t;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::sign_aware >
{
    typedef typename FORMATTER::formatter_sign_aware_t formatter_t;
};

template < typename FORMATTER, format_alignment ALIGNMENT >
using aligned_formatter_t = typename aligned_formatter< FORMATTER, ALIGNMENT >::formatter_t;

template < typename T, typename... ARGS, u32... PATTERN_INDICES, u32... ARGUMENT_INDICES >
u32 format(char* destination, u32 destination_length, index_sequence< PATTERN_INDICES... >,
           index_sequence< ARGUMENT_INDICES... >, ARGS&&... arguments)
{
    constexpr T                   format {};
    constexpr u32                 pattern_count           = sizeof...(PATTERN_INDICES);
    constexpr format_pattern_info patterns[pattern_count] = {
        get_format_info< T, PATTERN_INDICES,
                         decltype(format_as(minitl::forward< ARGS >(arguments)))... >(format)...};
    constexpr bool arg_used[]
        = {is_index_in_list< ARGUMENT_INDICES, u32(sizeof...(ARGS)),
                             patterns[PATTERN_INDICES].argument_index... >()...};
    motor_forceuse(arg_used);  // no check needed here
    constexpr format_alignment alignments[]
        = {patterns[PATTERN_INDICES].options.width == 0
               ? format_alignment::none
               : (patterns[PATTERN_INDICES].options.align == '<'
                      ? format_alignment::left
                      : (patterns[PATTERN_INDICES].options.align == '>'
                             ? format_alignment::right
                             : (patterns[PATTERN_INDICES].options.align == '^'
                                    ? format_alignment::center
                                    : format_alignment::sign_aware)))...};
    constexpr auto formatters
        = make_tuple(aligned_formatter_t< formatter< patterns[PATTERN_INDICES].options.formatter >,
                                          alignments[PATTERN_INDICES] >()...);

    u32 lengths[pattern_count] = {
        get< PATTERN_INDICES >(formatters)
            .length(get< patterns[PATTERN_INDICES].argument_index >(arguments..., brace_format {}),
                    patterns[PATTERN_INDICES].options)...};

    u32 offset    = 0;
    u32 offsets[] = {
        offset = fill_buffer< T >(
            destination, destination_length, offset, patterns[PATTERN_INDICES],
            lengths[PATTERN_INDICES], get< patterns[PATTERN_INDICES].argument_index >(formatters),
            get< patterns[PATTERN_INDICES].argument_index >(arguments..., brace_format {}))...};
    motor_forceuse(offsets);

    u32  max_size       = destination_length - offset;
    u32  segment_length = format.size() - patterns[pattern_count - 1].pattern_end;
    bool overflow       = segment_length > max_size;
    segment_length      = overflow ? max_size : segment_length;
    memcpy(destination + offset, &format[patterns[pattern_count - 1].pattern_end], segment_length);
    offset += segment_length;
    if(!overflow)
    {
        return offset - 1;
    }
    else
    {
        destination[destination_length - 4] = '.';
        destination[destination_length - 3] = '.';
        destination[destination_length - 2] = '.';
        destination[destination_length - 1] = '\0';
        return destination_length - 1;
    }
}

formatter< '{' > format_as(format_details::brace_format);

}  // namespace format_details

template < u32 SIZE, typename T, typename... ARGS >
MOTOR_ALWAYS_INLINE format_buffer< SIZE > format(T format_string, ARGS&&... arguments)
{
    format_buffer< SIZE > result;
    format_to(result.buffer, SIZE, format_string, minitl::forward< ARGS >(arguments)...);
    return result;
}

template < typename T, typename... ARGS >
MOTOR_ALWAYS_INLINE u32 format_to(char* destination, u32 length, T format_string,
                                  ARGS&&... arguments)
{
    motor_forceuse(format_string);
    constexpr u32 pattern_count = format_details::count_patterns(T {});

    return format_details::format< T >(destination, length, make_index_sequence< pattern_count >(),
                                       make_index_sequence< sizeof...(ARGS) >(),
                                       minitl::forward< ARGS >(arguments)...);
}

}  // namespace minitl

#endif
