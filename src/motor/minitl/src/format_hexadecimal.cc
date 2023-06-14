/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <string.h>

namespace minitl { namespace format_details { namespace hexadecimal_format {

static inline u64 format_hexadecimal_8(u32 number)
{
    u64 result = number;
    result |= result << (32 + 16);
    result >>= 16;
    result &= 0x0000ffff0000ffff;
    result |= result << (16 + 8);
    result >>= 8;
    result &= 0x00ff00ff00ff00ff;
    result |= result << (8 + 4);
    result >>= 4;
    result &= 0x0f0f0f0f0f0f0f0f;
    return result;
}

template < u32 WORD_COUNT >
static inline u32 format_hexadecimal_generic(char* destination, u64 number, char a)
{
    const u64 zero_string = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                             | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');

    if(WORD_COUNT >= 2 && number >> 32)
    {
        u64 result = format_hexadecimal_8(u32(number >> 32));
        u32 digit_count;
        for(digit_count = 8; digit_count > 1; --digit_count)
        {
            if(result & 0x0f) break;
            result >>= 8;
        }
        /* adds 6 so every digit >= 10 will have their bit 5 set */
        u64 above10 = result + 0x0606060606060606;
        above10 >>= 4;
        above10 &= 0x0101010101010101;
        result += zero_string;
        result += char(a - '9' - 1) * above10;
        memcpy(destination, &result, sizeof(result));

        destination += digit_count;
        result  = format_hexadecimal_8(u32(number & 0xffffffff));
        above10 = result + 0x0606060606060606;
        above10 >>= 4;
        above10 &= 0x0101010101010101;
        result += zero_string;
        result += char(a - '9' - 1) * above10;
        memcpy(destination, &result, sizeof(result));
        return digit_count + 8;
    }
    else
    {
        u64 result = format_hexadecimal_8(u32(number & 0xffffffff));
        u32 digit_count;
        for(digit_count = 8; digit_count > 1; --digit_count)
        {
            if(result & 0x0f) break;
            result >>= 8;
        }
        /* adds 6 so every digit >= 10 will have their bit 5 set */
        u64 above10 = result + 0x0606060606060606;
        above10 >>= 4;
        above10 &= 0x0101010101010101;
        result += zero_string;
        result += char(a - '9' - 1) * above10;
        memcpy(destination, &result, sizeof(result));
        return digit_count;
    }
}

motor_api(MINITL) u32 format_hexadecimal_whole(char* destination, u32 number)
{
    const u64 zero_string = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                             | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');
    u64       str, above10;

    str     = format_hexadecimal_8(number);
    above10 = str + 0x0606060606060606;
    above10 >>= 4;
    above10 &= 0x0101010101010101;
    str += zero_string;
    str += char('a' - '9' - 1) * above10;
    memcpy(destination, &str, sizeof(str));
    return 8;
}

motor_api(MINITL) u32 format_hexadecimal_whole(char* destination, u64 number)
{
    const u64 zero_string = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                             | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');
    u64       str, above10;

    str     = format_hexadecimal_8(u32(number >> 32));
    above10 = str + 0x0606060606060606;
    above10 >>= 4;
    above10 &= 0x0101010101010101;
    str += zero_string;
    str += char('a' - '9' - 1) * above10;
    memcpy(destination, &str, sizeof(str));
    destination += 8;
    str     = format_hexadecimal_8(u32(number & 0xffffffff));
    above10 = str + 0x0606060606060606;
    above10 >>= 4;
    above10 &= 0x0101010101010101;
    str += zero_string;
    str += char('a' - '9' - 1) * above10;
    memcpy(destination + 8, &str, sizeof(str));
    return 16;
}

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
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return format_hexadecimal_generic< 1 + sizeof(UNSIGNED_T) / 8 >(destination, value, a)
           + add_sign + options.alternate * 2;
}

template < typename T, typename UNSIGNED_T,
           enable_if_t< is_same< T, UNSIGNED_T >::value, int > X = true >
static MOTOR_ALWAYS_INLINE u32 format_arg_generic(char* destination, T number,
                                                  const format_options& options)
{
    u32 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return format_hexadecimal_generic< 1 + sizeof(UNSIGNED_T) / 8 >(destination, number, a)
           + add_sign + options.alternate * 2;
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

}}}  // namespace minitl::format_details::hexadecimal_format
