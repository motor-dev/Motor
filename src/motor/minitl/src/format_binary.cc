/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/format.hh>
#include <string.h>

namespace minitl { namespace format_details { namespace binary_format {

static inline u64 format_binary_8(u8 number)
{
    u64 result = number;
    result |= result << (32 + 4);
    result >>= 4;
    result &= 0x0000000f0000000f;
    result |= result << (16 + 2);
    result >>= 2;
    result &= 0x0003000300030003;
    result |= result << (8 + 1);
    result >>= 1;
    result &= 0x0101010101010101;
    return result;
}

template < u32 BYTE_COUNT >
static inline u32 format_binary_generic(char* destination, u64 number)
{
    const u64 zero_string = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                             | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');

    for(u32 highest = BYTE_COUNT - 1; highest > 0; --highest)
    {
        if(number >> (8 * highest))
        {
            u64 result = format_binary_8(u8(number >> (8 * highest)));
            u32 digit_count;
            for(digit_count = 8; digit_count > 1; --digit_count)
            {
                if(result & 0x01) break;
                result >>= 8;
            }
            result += zero_string;
            memcpy(destination, &result, sizeof(result));
            destination += digit_count;
            for(u32 i = highest - 1; i > 0; --i)
            {
                result = format_binary_8(u8((number >> (8 * i)) & 0xff));
                result += zero_string;
                memcpy(destination, &result, sizeof(result));
                destination += 8;
            }
            result = format_binary_8(u8(number & 0xff));
            result += zero_string;
            memcpy(destination, &result, sizeof(result));
            return digit_count + 8 * highest;
        }
    }
    u64 result = format_binary_8(u8(number));
    u32 digit_count;
    for(digit_count = 8; digit_count > 1; --digit_count)
    {
        if(result & 0x01) break;
        result >>= 8;
    }
    result += zero_string;
    memcpy(destination, &result, sizeof(result));
    return digit_count;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed char number, const format_options& options)
{
    u32           negative       = u32(number < 0);
    u32           negative_mask  = ~(negative - 1);
    u32           add_sign       = negative | (options.sign == '+');
    unsigned char negative_value = ~number + 1;
    unsigned char value          = number + ((negative_value - number) & negative_mask);
    *destination                 = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed short number, const format_options& options)
{
    u32            negative       = u32(number < 0);
    u32            negative_mask  = ~(negative - 1);
    u32            add_sign       = negative | (options.sign == '+');
    unsigned short negative_value = ~number + 1;
    unsigned short value          = number + ((negative_value - number) & negative_mask);
    *destination                  = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed int number, const format_options& options)
{
    u32          negative       = u32(number < 0);
    u32          negative_mask  = ~(negative - 1);
    u32          add_sign       = negative | (options.sign == '+');
    unsigned int negative_value = ~number + 1;
    unsigned int value          = number + ((negative_value - number) & negative_mask);
    *destination                = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    *destination = char('+' + (('-' - '+') & negative_mask));

    return format_binary_generic< sizeof(number) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed long number, const format_options& options)
{
    u32           negative       = u32(number < 0);
    u64           negative_mask  = ~(u64(negative) - 1);
    u32           add_sign       = negative | (options.sign == '+');
    unsigned long negative_value = ~number + 1;
    unsigned long value          = number + ((negative_value - number) & negative_mask);
    *destination                 = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, signed long long number, const format_options& options)
{
    u32                negative       = u32(number < 0);
    u64                negative_mask  = ~(u64(negative) - 1);
    u32                add_sign       = negative | (options.sign == '+');
    unsigned long long negative_value = ~number + 1;
    unsigned long long value          = number + ((negative_value - number) & negative_mask);
    *destination                      = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned char number, const format_options& options)
{
    u32 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, number) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned short number, const format_options& options)
{
    u32 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, number) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned int number, const format_options& options)
{
    u32 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, number) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned long number, const format_options& options)
{
    u32 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, number) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned long long number, const format_options& options)
{
    u32 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(number) >(destination, number) + add_sign
           + 2 * options.alternate;
}

}}}  // namespace minitl::format_details::binary_format
