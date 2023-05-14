/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/minitl/format.hh>
#include <motor/minitl/weakptr.hh>
#include <cstring>

namespace minitl { namespace format_details {

bool invalid_format(const char* reason)
{
    motor_assert_format(false, "invalid format: {0}", reason);
    return false;
}

#ifndef MOTOR_LITTLE_ENDIAN
#    error Code currently only working on little endian!
#endif

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

static inline u32 format_decimal_4(u32 number)
{
    u32 intermediate = (number * 5243 >> 19);
    number           = intermediate | ((number - intermediate * 100) << 16);
    intermediate     = ((number * 103) >> 10) & 0x003f003f;
    number           = intermediate | ((number - intermediate * 10) << 8);

    return number;
}

static inline u64 format_decimal_8(u64 number)
{
    u64 intermediate = (number * 5243 >> 19) & 0x00001fff00001fff;
    number           = intermediate | ((number - intermediate * 100) << 16);
    intermediate     = ((number * 103) >> 10) & 0x003f003f003f003f;
    number           = intermediate | ((number - intermediate * 10) << 8);

    return number;
}

namespace binary_format {

motor_api(MINITL) u32 format_arg(char* destination, i8 number, const format_options& options)
{
    u32 negative       = u32(number < 0);
    u32 negative_mask  = ~(negative - 1);
    u32 add_sign       = negative | (options.sign == '+');
    u8  negative_value = ~number + 1;
    u8  value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(u8) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, i16 number, const format_options& options)
{
    u32 negative       = u32(number < 0);
    u32 negative_mask  = ~(negative - 1);
    u32 add_sign       = negative | (options.sign == '+');
    u16 negative_value = ~number + 1;
    u16 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(u16) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, i32 number, const format_options& options)
{
    u32 negative       = u32(number < 0);
    u32 negative_mask  = ~(negative - 1);
    u32 add_sign       = negative | (options.sign == '+');
    u32 negative_value = ~number + 1;
    u32 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    *destination = char('+' + (('-' - '+') & negative_mask));

    return format_binary_generic< sizeof(u32) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, i64 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(u64) >(destination, value) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u8 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(u8) >(destination, number) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u16 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(u16) >(destination, number) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u32 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(u32) >(destination, number) + add_sign
           + 2 * options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u64 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    return format_binary_generic< sizeof(u64) >(destination, number) + add_sign
           + 2 * options.alternate;
}

}  // namespace binary_format

namespace octal_format {

motor_api(MINITL) u32 format_arg(char* destination, i8 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 1 >(destination, value) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, i16 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 1 >(destination, value) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, i32 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 2 >(destination, value) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, i64 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 3 >(destination, value) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u8 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 1 >(destination, number) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u16 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 1 >(destination, number) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u32 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 2 >(destination, number) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u64 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    return format_octal_generic< 3 >(destination, number) + add_sign + options.alternate;
}

}  // namespace octal_format

namespace decimal_format {

static inline u32 format_decimal(char* destination, u8 number, char sign, u32 add_sign)
{
    const u32 zero_string
        = (('0' << 24) | ('0' << 16) | ('0' << 8) | '0') + char((sign - '0') & (~add_sign + 1));

    u32 digit_count = add_sign + 1;
    digit_count += number >= 10;
    digit_count += number >= 100;
    u32 number32 = format_decimal_4(number);
    number32 >>= (4 - digit_count) * 8;
    number32 += zero_string;
    memcpy(destination, &number32, sizeof(number32));
    // destination[digitCount] = 0;
    return digit_count;
}

static inline u32 format_decimal(char* destination, u16 number, char sign, u32 add_sign)
{
    const u64 zero_string = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                             | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0')
                            + char((sign - '0') & (~add_sign + 1));

    u64 number64;
    u32 digit_count = add_sign;
    if(number < 10000)
    {
        number64 = 0;
        digit_count += number >= 10;
        digit_count += number >= 100;
        digit_count += number >= 1000;
        digit_count++;
    }
    else
    {
        number64 = number / 10000;
        number %= 10000;
        digit_count += 5;
    }
    number64 |= (u64)number << 32;
    number64 = format_decimal_8(number64);
    number64 >>= (8 - digit_count) * 8;
    number64 += zero_string;
    memcpy(destination, &number64, sizeof(number64));
    // destination[digitCount] = 0;
    return digit_count;
}

static inline u32 format_decimal(char* destination, u32 number, char sign, u32 add_sign)
{
    const u64 zero_string = (u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                            | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0';
    const u64 zero_sign_string = zero_string + char((sign - '0') & (~add_sign + 1));

    if((number < 10000000) || (number < 100000000 && !add_sign))
    {
        /* can write 8 chars in one */
        u64 number64;
        u32 digit_count = add_sign;
        if(number < 10000)
        {
            number64 = 0;
            digit_count += number >= 10;
            digit_count += number >= 100;
            digit_count += number >= 1000;
            digit_count++;
        }
        else
        {
            number64 = number / 10000;
            number %= 10000;
            digit_count += 5;
            digit_count += number64 >= 10;
            digit_count += number64 >= 100;
            digit_count += number64 >= 1000;
        }
        number64 |= (u64)number << 32;
        number64 = format_decimal_8(number64);
        number64 >>= (8 - digit_count) * 8;
        number64 += zero_sign_string;
        memcpy(destination, &number64, sizeof(number64));
        // destination[digitCount] = 0;
        return digit_count;
    }
    else
    {
        u32 digit_count = add_sign;
        u32 top         = number / 100000000;
        number          = number % 100000000;
        digit_count += top >= 1;
        digit_count += top >= 10;
        top = format_decimal_4(top);
        top >>= 8 * (4 - digit_count);
        top = top + u32(zero_sign_string);
        memcpy(destination, &top, sizeof(top));

        u64 number64 = number / 10000;
        number64 |= (u64)(number % 10000) << 32;
        number64 = format_decimal_8(number64);
        number64 += zero_string;

        memcpy(destination + digit_count, &number64, sizeof(number64));

        return digit_count + 8;
    }
}

static inline u32 format_decimal(char* destination, u64 number, char sign, u32 add_sign)
{
    const u64 zero_string      = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                             | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');
    const u64 zero_sign_string = zero_string + char((sign - '0') & (~add_sign + 1));

    if((number < 10000000) || (number < 100000000 && !add_sign))
    {
        /* can write 8 chars in one */
        u64 number64;
        u32 digit_count = add_sign;
        if(number < 10000)
        {
            number64 = 0;
            digit_count += number >= 10;
            digit_count += number >= 100;
            digit_count += number >= 1000;
            digit_count++;
        }
        else
        {
            number64 = number / 10000;
            number %= 10000;
            digit_count += 5;
            digit_count += number64 >= 10;
            digit_count += number64 >= 100;
            digit_count += number64 >= 1000;
        }
        number64 |= (u64)number << 32;
        number64 = format_decimal_8(number64);
        number64 >>= (8 - digit_count) * 8;
        number64 += zero_sign_string;
        memcpy(destination, &number64, sizeof(number64));
        // destination[digitCount] = 0;
        return digit_count;
    }
    else if(number < 100000000)
    {
        *destination = sign;
        u64 number64 = number / 10000;
        number64 |= (u64)(number % 10000) << 32;
        number64 = format_decimal_8(number64);
        number64 += zero_string;
        memcpy(destination + 1, &number64, sizeof(number64));

        return 9;
    }
    else
    {
        u32 digit_count = format_decimal(destination, number / 100000000, sign, add_sign);
        number          = number % 100000000;
        u64 number64    = number / 10000;
        number64 |= (u64)(number % 10000) << 32;
        number64 = format_decimal_8(number64);
        number64 += zero_string;

        memcpy(destination + digit_count, &number64, sizeof(number64));

        return digit_count + 8;
    }
}

motor_api(MINITL) u32 format_arg(char* destination, i8 number, const format_options& options)
{
    u64  negative       = u32(number < 0);
    u64  negative_mask  = ~(negative - 1);
    u64  add_sign       = negative | (options.sign == '+');
    u64  negative_value = ~number + 1;
    u64  value          = number + ((negative_value - number) & negative_mask);
    char sign           = char('+' + (('-' - '+') & negative_mask));
    return format_decimal(destination, value, sign, add_sign);
}

motor_api(MINITL) u32 format_arg(char* destination, i16 number, const format_options& options)
{
    u64  negative       = u32(number < 0);
    u64  negative_mask  = ~(negative - 1);
    u64  add_sign       = negative | (options.sign == '+');
    u64  negative_value = ~number + 1;
    u64  value          = number + ((negative_value - number) & negative_mask);
    char sign           = char('+' + (('-' - '+') & negative_mask));
    return format_decimal(destination, value, sign, add_sign);
}

motor_api(MINITL) u32 format_arg(char* destination, i32 number, const format_options& options)
{
    u64  negative       = u32(number < 0);
    u64  negative_mask  = ~(negative - 1);
    u64  add_sign       = negative | (options.sign == '+');
    u64  negative_value = ~number + 1;
    u64  value          = number + ((negative_value - number) & negative_mask);
    char sign           = char('+' + (('-' - '+') & negative_mask));
    return format_decimal(destination, value, sign, add_sign);
}

motor_api(MINITL) u32 format_arg(char* destination, i64 number, const format_options& options)
{
    u64  negative       = u32(number < 0);
    u64  negative_mask  = ~(negative - 1);
    u64  add_sign       = negative | (options.sign == '+');
    u64  negative_value = ~number + 1;
    u64  value          = number + ((negative_value - number) & negative_mask);
    char sign           = char('+' + (('-' - '+') & negative_mask));
    return format_decimal(destination, value, sign, add_sign);
}

motor_api(MINITL) u32 format_arg(char* destination, u8 number, const format_options& options)
{
    return format_decimal(destination, number, options.sign, options.sign == '+');
}

motor_api(MINITL) u32 format_arg(char* destination, u16 number, const format_options& options)
{
    return format_decimal(destination, number, options.sign, options.sign == '+');
}

motor_api(MINITL) u32 format_arg(char* destination, u32 number, const format_options& options)
{
    return format_decimal(destination, number, options.sign, options.sign == '+');
}

motor_api(MINITL) u32 format_arg(char* destination, u64 number, const format_options& options)
{
    return format_decimal(destination, number, options.sign, options.sign == '+');
}

}  // namespace decimal_format

namespace hexadecimal_format {

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

motor_api(MINITL) u32 format_arg(char* destination, i8 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return format_hexadecimal_generic< 1 >(destination, value, a) + add_sign
           + options.alternate * 2;
}

motor_api(MINITL) u32 format_arg(char* destination, i16 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return format_hexadecimal_generic< 1 >(destination, value, a) + add_sign
           + options.alternate * 2;
}

motor_api(MINITL) u32 format_arg(char* destination, i32 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return format_hexadecimal_generic< 1 >(destination, value, a) + add_sign
           + options.alternate * 2;
}

motor_api(MINITL) u32 format_arg(char* destination, i64 number, const format_options& options)
{
    u64 negative       = u32(number < 0);
    u64 negative_mask  = ~(negative - 1);
    u64 add_sign       = negative | (options.sign == '+');
    u64 negative_value = ~number + 1;
    u64 value          = number + ((negative_value - number) & negative_mask);
    *destination       = char('+' + (('-' - '+') & negative_mask));
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return format_hexadecimal_generic< 2 >(destination, value, a) + add_sign + options.alternate;
}

motor_api(MINITL) u32 format_arg(char* destination, u8 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return options.sign + format_hexadecimal_generic< 1 >(destination, number, a) + add_sign
           + options.alternate * 2;
}

motor_api(MINITL) u32 format_arg(char* destination, u16 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return options.sign + format_hexadecimal_generic< 1 >(destination, number, a) + add_sign
           + options.alternate * 2;
}

motor_api(MINITL) u32 format_arg(char* destination, u32 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return options.sign + format_hexadecimal_generic< 1 >(destination, number, a) + add_sign
           + options.alternate * 2;
}

motor_api(MINITL) u32 format_arg(char* destination, u64 number, const format_options& options)
{
    u64 add_sign = options.sign == '+';
    *destination = '+';
    destination += add_sign;
    *destination = '0';
    destination += options.alternate;
    *destination = options.formatter;
    destination += options.alternate;
    char a = char('a' + options.formatter - 'x');
    return options.sign + format_hexadecimal_generic< 2 >(destination, number, a) + add_sign
           + options.alternate * 2;
}

}  // namespace hexadecimal_format

namespace pointer_format {

motor_api(MINITL) u32
    format_arg(char* destination, const void* pointer, const format_options& options)
{
    union
    {
        const void* pointer;
        u64         number;
    } x          = {pointer};
    u32 result   = options.alternate;
    *destination = '@';
    destination += result;
#if _LP64
    result += hexadecimal_format::format_hexadecimal_whole(destination + result, x.number);
#else
    result += hexadecimal_format::format_hexadecimal_whole(destination + result, u32(x.number));
#endif
    return result;
}

}  // namespace pointer_format

namespace string_format {

motor_api(MINITL) u32 format_arg(char* destination, bool_wrapper value,
                                 const format_options& options, u32 reserved_length)
{
    motor_forceuse(options);
    if(value)
        memcpy(destination, "true", 4);   // NOLINT(bugprone-not-null-terminated-result)
    else
        memcpy(destination, "false", 5);  // NOLINT(bugprone-not-null-terminated-result)
    return reserved_length;
}

motor_api(MINITL) u32
    format_arg_partial(char* destination, bool_wrapper value, const format_options& options,
                       u32 reserved_length, u32 max_capacity)
{
    motor_forceuse(options);
    motor_forceuse(reserved_length);
    if(value)
        memcpy(destination, "true", max_capacity);
    else
        memcpy(destination, "false", max_capacity);
    return max_capacity;
}

}  // namespace string_format

}}  // namespace minitl::format_details
