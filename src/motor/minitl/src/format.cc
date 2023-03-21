/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/minitl/format.hh>

namespace minitl { namespace format_details {

bool invalid_format(const char* reason)
{
    motor_assert_format(false, "invalid format: {0}", reason);
    return false;
}

#ifndef MOTOR_LITTLEENDIAN
#    error Code currently only working on little endian!
#endif

static inline u64 formatBinary_8(u8 number)
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
static inline u32 formatBinaryGeneric(char* destination, u64 number, char sign, u32 addSign)
{
    const u64 zeroString = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                            | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');
    *destination         = sign;
    destination += addSign;

    for(u32 highest = BYTE_COUNT - 1; highest > 0; --highest)
    {
        if(number >> (8 * highest))
        {
            u64 result = formatBinary_8(number >> (8 * highest));
            u32 digitCount;
            for(digitCount = 8; digitCount > 1; --digitCount)
            {
                if(result & 0x01) break;
                result >>= 8;
            }
            result += zeroString;
            memcpy(destination, &result, sizeof(result));
            destination += digitCount;
            for(u32 i = highest - 1; i > 0; --i)
            {
                result = formatBinary_8(number >> (8 * i));
                result += zeroString;
                memcpy(destination, &result, sizeof(result));
                destination += 8;
            }
            result = formatBinary_8(number);
            result += zeroString;
            memcpy(destination, &result, sizeof(result));
            return digitCount + addSign + 8 * highest;
        }
    }
    u64 result = formatBinary_8(number);
    u32 digitCount;
    for(digitCount = 8; digitCount > 1; --digitCount)
    {
        if(result & 0x01) break;
        result >>= 8;
    }
    result += zeroString;
    memcpy(destination, &result, sizeof(result));
    return digitCount + addSign;
}

static inline u64 formatOctal_8(u32 number)
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
static inline u32 formatOctalGeneric(char* destination, u64 number, char sign, u32 addSign)
{
    const u64 zeroString = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                            | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');
    *destination         = sign;
    destination += addSign;

    for(u32 highest = WORD_COUNT - 1; highest > 0; --highest)
    {
        if(number >> (24 * highest))
        {
            u64 result = formatOctal_8(number >> (24 * highest));
            u32 digitCount;
            for(digitCount = 8; digitCount > 1; --digitCount)
            {
                if(result & 0x07) break;
                result >>= 8;
            }
            result += zeroString;
            memcpy(destination, &result, sizeof(result));
            destination += digitCount;
            for(u32 i = highest - 1; i > 0; --i)
            {
                result = formatOctal_8(number >> (24 * i));
                result += zeroString;
                memcpy(destination, &result, sizeof(result));
                destination += 8;
            }
            result = formatOctal_8(number);
            result += zeroString;
            memcpy(destination, &result, sizeof(result));
            return digitCount + addSign + 8 * highest;
        }
    }
    u64 result = formatOctal_8(number);
    u32 digitCount;
    for(digitCount = 8; digitCount > 1; --digitCount)
    {
        if(result & 0x07) break;
        result >>= 8;
    }
    result += zeroString;
    memcpy(destination, &result, sizeof(result));
    return digitCount + addSign;
}

static inline u64 formatHexadecimal_8(u32 number)
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
static inline u32 formatHexadecimalGeneric(char* destination, u64 number, char sign, u32 addSign,
                                           char a)
{
    const u64 zeroString = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                            | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');
    *destination         = sign;
    destination += addSign;

    if(WORD_COUNT >= 2 && number >> 32)
    {
        u64 result = formatHexadecimal_8(number >> 32);
        u32 digitCount;
        for(digitCount = 8; digitCount > 1; --digitCount)
        {
            if(result & 0x0f) break;
            result >>= 8;
        }
        /* adds 6 so every digit >= 10 will have their bit 5 set */
        u64 above10 = result + 0x0606060606060606;
        above10 >>= 4;
        above10 &= 0x0101010101010101;
        result += zeroString;
        result += char(a - '9' - 1) * above10;
        memcpy(destination, &result, sizeof(result));

        destination += digitCount;
        result  = formatHexadecimal_8(number);
        above10 = result + 0x0606060606060606;
        above10 >>= 4;
        above10 &= 0x0101010101010101;
        result += zeroString;
        result += char(a - '9' - 1) * above10;
        memcpy(destination, &result, sizeof(result));
        return digitCount + addSign + 8;
    }
    else
    {
        u64 result = formatHexadecimal_8(number);
        u32 digitCount;
        for(digitCount = 8; digitCount > 1; --digitCount)
        {
            if(result & 0x0f) break;
            result >>= 8;
        }
        /* adds 6 so every digit >= 10 will have their bit 5 set */
        u64 above10 = result + 0x0606060606060606;
        above10 >>= 4;
        above10 &= 0x0101010101010101;
        result += zeroString;
        result += char(a - '9' - 1) * above10;
        memcpy(destination, &result, sizeof(result));
        return digitCount + addSign;
    }
}

static inline u32 formatDecimal_4(u32 number)
{
    u32 intermediate = (number * 5243 >> 19);
    number           = intermediate | ((number - intermediate * 100) << 16);
    intermediate     = ((number * 103) >> 10) & 0x003f003f;
    number           = intermediate | ((number - intermediate * 10) << 8);

    return number;
}

static inline u64 formatDecimal_8(u64 number)
{
    u64 intermediate = (number * 5243 >> 19) & 0x00001fff00001fff;
    number           = intermediate | ((number - intermediate * 100) << 16);
    intermediate     = ((number * 103) >> 10) & 0x003f003f003f003f;
    number           = intermediate | ((number - intermediate * 10) << 8);

    return number;
}

motor_api(MINITL) u32 format_binary(char* destination, u8 number, char sign, u32 addSign)
{
    return formatBinaryGeneric< sizeof(u8) >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_binary(char* destination, u16 number, char sign, u32 addSign)
{
    return formatBinaryGeneric< sizeof(u16) >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_binary(char* destination, u32 number, char sign, u32 addSign)
{
    return formatBinaryGeneric< sizeof(u32) >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_binary(char* destination, u64 number, char sign, u32 addSign)
{
    return formatBinaryGeneric< sizeof(u64) >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_octal(char* destination, u8 number, char sign, u32 addSign)
{
    return formatOctalGeneric< 1 >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_octal(char* destination, u16 number, char sign, u32 addSign)
{
    return formatOctalGeneric< 1 >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_octal(char* destination, u32 number, char sign, u32 addSign)
{
    return formatOctalGeneric< 2 >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_octal(char* destination, u64 number, char sign, u32 addSign)
{
    return formatOctalGeneric< 3 >(destination, number, sign, addSign);
}

motor_api(MINITL) u32 format_decimal(char* destination, u8 number, char sign, u32 addSign)
{
    const u32 zeroString
        = (('0' << 24) | ('0' << 16) | ('0' << 8) | '0') + char((sign - '0') & -addSign);

    u32 digitCount = addSign + 1;
    digitCount += number >= 10;
    digitCount += number >= 100;
    u32 number32 = formatDecimal_4(number);
    number32 >>= (4 - digitCount) * 8;
    number32 += zeroString;
    memcpy(destination, &number32, sizeof(number32));
    // destination[digitCount] = 0;
    return digitCount;
}

motor_api(MINITL) u32 format_decimal(char* destination, u16 number, char sign, u32 addSign)
{
    const u64 zeroString = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                            | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0')
                           + char((sign - '0') & -addSign);

    u64 number64;
    u32 digitCount = addSign;
    if(number < 10000)
    {
        number64 = 0;
        digitCount += number >= 10;
        digitCount += number >= 100;
        digitCount += number >= 1000;
        digitCount++;
    }
    else
    {
        number64 = number / 10000;
        number %= 10000;
        digitCount += 5;
    }
    number64 |= (u64)number << 32;
    number64 = formatDecimal_8(number64);
    number64 >>= (8 - digitCount) * 8;
    number64 += zeroString;
    memcpy(destination, &number64, sizeof(number64));
    // destination[digitCount] = 0;
    return digitCount;
}

motor_api(MINITL) u32 format_decimal(char* destination, u32 number, char sign, u32 addSign)
{
    const u64 zeroString = (u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40) | (u64('0') << 32)
                           | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0';
    const u64 zeroSignString = zeroString + char((sign - '0') & -addSign);

    if((number < 10000000) || (number < 100000000 && !addSign))
    {
        /* can write 8 chars in one */
        u64 number64;
        u32 digitCount = addSign;
        if(number < 10000)
        {
            number64 = 0;
            digitCount += number >= 10;
            digitCount += number >= 100;
            digitCount += number >= 1000;
            digitCount++;
        }
        else
        {
            number64 = number / 10000;
            number %= 10000;
            digitCount += 5;
            digitCount += number64 >= 10;
            digitCount += number64 >= 100;
            digitCount += number64 >= 1000;
        }
        number64 |= (u64)number << 32;
        number64 = formatDecimal_8(number64);
        number64 >>= (8 - digitCount) * 8;
        number64 += zeroSignString;
        memcpy(destination, &number64, sizeof(number64));
        // destination[digitCount] = 0;
        return digitCount;
    }
    else
    {
        u32 digitCount = addSign;
        u32 top        = number / 100000000;
        number         = number % 100000000;
        digitCount += top >= 1;
        digitCount += top >= 10;
        top = formatDecimal_4(top);
        top >>= 8 * (4 - digitCount);
        top = top + zeroSignString;
        memcpy(destination, &top, sizeof(top));

        u64 number64 = number / 10000;
        number64 |= (u64)(number % 10000) << 32;
        number64 = formatDecimal_8(number64);
        number64 += zeroString;

        memcpy(destination + digitCount, &number64, sizeof(number64));

        return digitCount + 8;
    }
}

motor_api(MINITL) u32 format_decimal(char* destination, u64 number, char sign, u32 addSign)
{
    const u64 zeroString     = ((u64('0') << 56) | (u64('0') << 48) | (u64('0') << 40)
                            | (u64('0') << 32) | ('0' << 24) | ('0' << 16) | ('0' << 8) | '0');
    const u64 zeroSignString = zeroString + char((sign - '0') & -addSign);

    if((number < 10000000) || (number < 100000000 && !addSign))
    {
        /* can write 8 chars in one */
        u64 number64;
        u32 digitCount = addSign;
        if(number < 10000)
        {
            number64 = 0;
            digitCount += number >= 10;
            digitCount += number >= 100;
            digitCount += number >= 1000;
            digitCount++;
        }
        else
        {
            number64 = number / 10000;
            number %= 10000;
            digitCount += 5;
            digitCount += number64 >= 10;
            digitCount += number64 >= 100;
            digitCount += number64 >= 1000;
        }
        number64 |= (u64)number << 32;
        number64 = formatDecimal_8(number64);
        number64 >>= (8 - digitCount) * 8;
        number64 += zeroSignString;
        memcpy(destination, &number64, sizeof(number64));
        // destination[digitCount] = 0;
        return digitCount;
    }
    else if(number < 100000000)
    {
        *destination = sign;
        u64 number64 = number / 10000;
        number64 |= (u64)(number % 10000) << 32;
        number64 = formatDecimal_8(number64);
        number64 += zeroString;
        memcpy(destination + 1, &number64, sizeof(number64));

        return 9;
    }
    else
    {
        u32 digitCount = format_decimal(destination, number / 100000000, sign, addSign);
        number         = number % 100000000;
        u64 number64   = number / 10000;
        number64 |= (u64)(number % 10000) << 32;
        number64 = formatDecimal_8(number64);
        number64 += zeroString;

        memcpy(destination + digitCount, &number64, sizeof(number64));

        return digitCount + 8;
    }
}

motor_api(MINITL) u32
    format_hexadecimal(char* destination, u8 number, char sign, u32 addSign, char a)
{
    return formatHexadecimalGeneric< 1 >(destination, number, sign, addSign, a);
}

motor_api(MINITL) u32
    format_hexadecimal(char* destination, u16 number, char sign, u32 addSign, char a)
{
    return formatHexadecimalGeneric< 1 >(destination, number, sign, addSign, a);
}

motor_api(MINITL) u32
    format_hexadecimal(char* destination, u32 number, char sign, u32 addSign, char a)
{
    return formatHexadecimalGeneric< 1 >(destination, number, sign, addSign, a);
}

motor_api(MINITL) u32
    format_hexadecimal(char* destination, u64 number, char sign, u32 addSign, char a)
{
    return formatHexadecimalGeneric< 2 >(destination, number, sign, addSign, a);
}

}}  // namespace minitl::format_details
