/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/format.hh>
#include <string.h>

namespace minitl { namespace format_details { namespace decimal_format {

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

template < typename T, typename UNSIGNED_T >
static MOTOR_ALWAYS_INLINE u32 format_arg_generic(char* destination, T number,
                                                  const format_options& options)
{
    auto       negative       = u32(number < 0);
    UNSIGNED_T negative_mask  = ~(UNSIGNED_T(negative) - 1);
    u32        add_sign       = negative | (options.sign == '+');
    UNSIGNED_T negative_value = ~number + 1;
    UNSIGNED_T value          = number + ((negative_value - number) & negative_mask);
    char       sign           = char('+' + (('-' - '+') & negative_mask));
    return format_decimal(destination, unsigned_integer_type_t< sizeof(value) >(value), sign,
                          add_sign);
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
    return format_decimal(destination, unsigned_integer_type_t< sizeof(number) >(number),
                          options.sign, options.sign == '+');
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned short number, const format_options& options)
{
    return format_decimal(destination, unsigned_integer_type_t< sizeof(number) >(number),
                          options.sign, options.sign == '+');
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned int number, const format_options& options)
{
    return format_decimal(destination, unsigned_integer_type_t< sizeof(number) >(number),
                          options.sign, options.sign == '+');
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned long number, const format_options& options)
{
    return format_decimal(destination, unsigned_integer_type_t< sizeof(number) >(number),
                          options.sign, options.sign == '+');
}

motor_api(MINITL) u32
    format_arg(char* destination, unsigned long long number, const format_options& options)
{
    return format_decimal(destination, unsigned_integer_type_t< sizeof(number) >(number),
                          options.sign, options.sign == '+');
}

}}}  // namespace minitl::format_details::decimal_format
