/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/format.hh>
#include <string.h>

namespace minitl { namespace format_details { namespace octal_format {

static inline u64 format_octal_8(u32 number)
{
    u64 result = number & 0xffffff;
    result |= result << (32 + 12);
    result >>= 12;
    result &= 0x00000fff00000fff;
    result |= result << (16 + 6);
    result >>= 6;
    result &= 0x003f003f003f003f;
    result |= result << (8 + 3);
    result >>= 3;
    result &= 0x0707070707070707;
    return result;
}

template < u32 WORD_COUNT >
static inline u32 format_octal_generic(char* destination, u64 number)
{
    const u64 zero_string = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                             | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');

    for(u32 highest = WORD_COUNT - 1; highest > 0; --highest)
    {
        if(number >> (24 * highest))
        {
            u64 result = format_octal_8(u32(number >> (24 * highest)));
            u32 digit_count;
            for(digit_count = 8; digit_count > 1; --digit_count)
            {
                if(result & 0x07) break;
                result >>= 8;
            }
            result += zero_string;
            memcpy(destination, &result, sizeof(result));
            destination += digit_count;
            for(u32 i = highest - 1; i > 0; --i)
            {
                result = format_octal_8(u32((number >> (24 * i)) & 0xffffffff));
                result += zero_string;
                memcpy(destination, &result, sizeof(result));
                destination += 8;
            }
            result = format_octal_8(u32(number & 0xffffffff));
            result += zero_string;
            memcpy(destination, &result, sizeof(result));
            return digit_count + 8 * highest;
        }
    }
    u64 result = format_octal_8(u32(number));
    u32 digit_count;
    for(digit_count = 8; digit_count > 1; --digit_count)
    {
        if(result & 0x07) break;
        result >>= 8;
    }
    result += zero_string;
    memcpy(destination, &result, sizeof(result));
    return digit_count;
}

static constexpr u32 s_iteration_count[5] = {1, 1, 2, 2, 3};

template < typename T, typename UNSIGNED_T,
           enable_if_t< !is_same< T, UNSIGNED_T >::value, bool > X = true >
static MOTOR_ALWAYS_INLINE u32 format_arg_generic(char* destination, T number,
                                                  const format_options& options)
{
    auto       negative       = u32(number < 0);
    UNSIGNED_T negative_mask  = ~(UNSIGNED_T(negative) - 1);
    u32        add_sign       = negative | (options.sign == '+');
    UNSIGNED_T negative_value = ~number + 1;
    UNSIGNED_T value          = number + ((negative_value - number) & negative_mask);
    *destination              = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< s_iteration_count[sizeof(number) / 2] >(destination, value)
           + add_sign + options.alternate;
}

template < typename T, typename UNSIGNED_T,
           enable_if_t< is_same< T, UNSIGNED_T >::value, int > = true >
static MOTOR_ALWAYS_INLINE u32 format_arg_generic(char* destination, T number,
                                                  const format_options& options)
{
    u32 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 1 >(destination, number) + add_sign + options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed char number, const format_options& options)
{
    return format_arg_generic< signed char, unsigned char >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, signed short number, const format_options& options)
{
    return format_arg_generic< signed short, unsigned short >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, signed int number, const format_options& options)
{
    return format_arg_generic< signed int, unsigned int >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, signed long number, const format_options& options)
{
    return format_arg_generic< signed long, unsigned long >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, signed long long number, const format_options& options)
{
    return format_arg_generic< signed long long, unsigned long long >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned char number, const format_options& options)
{
    return format_arg_generic< unsigned char, unsigned char >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned short number, const format_options& options)
{
    return format_arg_generic< unsigned short, unsigned short >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned int number, const format_options& options)
{
    return format_arg_generic< unsigned int, unsigned int >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned long number, const format_options& options)
{
    return format_arg_generic< unsigned long, unsigned long >(destination, number, options);
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned long long number, const format_options& options)
{
    return format_arg_generic< unsigned long long, unsigned long long >(destination, number,
                                                                        options);
}

}}}  // namespace minitl::format_details::octal_format
