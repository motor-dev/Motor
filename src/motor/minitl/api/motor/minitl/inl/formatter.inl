/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_FORMATER_INL_
#define MOTOR_MINITL_FORMATER_INL_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/kernel/interlocked.hh>
#include <motor/minitl/format.hh>
#include <stdio.h>
#include <string.h>

namespace minitl {

template < typename T >
struct formatter< const T > : public formatter< T >
{
};

template < typename T >
struct formatter< T& > : public formatter< T >
{
};

template < typename T >
struct formatter< T&& > : public formatter< T >
{
};

namespace format_details {

motor_api(MINITL) u32 format_binary(char* destination, u8 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_binary(char* destination, u16 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_binary(char* destination, u32 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_binary(char* destination, u64 number, char sign, u32 addSign);

motor_api(MINITL) u32 format_octal(char* destination, u8 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_octal(char* destination, u16 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_octal(char* destination, u32 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_octal(char* destination, u64 number, char sign, u32 addSign);

motor_api(MINITL) u32 format_decimal(char* destination, u8 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_decimal(char* destination, u16 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_decimal(char* destination, u32 number, char sign, u32 addSign);
motor_api(MINITL) u32 format_decimal(char* destination, u64 number, char sign, u32 addSign);

motor_api(MINITL) u32
    format_hexadecimal(char* destination, u8 number, char sign, u32 addSign, char a);
motor_api(MINITL) u32
    format_hexadecimal(char* destination, u16 number, char sign, u32 addSign, char a);
motor_api(MINITL) u32
    format_hexadecimal(char* destination, u32 number, char sign, u32 addSign, char a);
motor_api(MINITL) u32
    format_hexadecimal(char* destination, u64 number, char sign, u32 addSign, char a);

template < typename T >
struct default_partial_formatter
{
    static u32 format_to_partial(char* destination, const T& value, const format_options& options,
                                 u32 reservedLength, u32 maximalLength)
    {
        char* buffer         = static_cast< char* >(malloca(reservedLength));
        u32   requiredLength = formatter< T >::format_to(buffer, value, options, reservedLength);
        maximalLength        = requiredLength < maximalLength ? requiredLength : maximalLength;
        memcpy(destination, buffer, maximalLength);
        freea(buffer);
        return maximalLength;
    }
};

template < typename T, typename UnsignedT >
struct numeric_formatter : public default_partial_formatter< T >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '>', '-', 'd', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'b' && options.format != 'B' && options.format != 'd'
           && options.format != 'o' && options.format != 'x' && options.format != 'X')
            return invalid_format("invalid format specifier for integer argument");
        if(options.sign != ' ' && options.sign != '+' && options.sign != '-')
            return invalid_format("invalid sign");
        if(options.align == '<' && options.signPadding)
            return invalid_format("sign-aware padding not allowed with left alignment");
        if(options.precision != 0) return invalid_format("precision not allowed for integer type");
        return true;
    }

    static constexpr u32 length(T value, const format_options& options)
    {
        motor_forceuse(value);
        static_assert(sizeof(T) <= 8, "numeric_formatter can handle up to 64bits integers");
        /* reserved space for base 10:
            1 byte   -> 4 (enough for +256)
            2 bytes  -> 6 (enough for +65535)
            4 bytes  -> 11 (enough for +2147483647)
            8 bytes  -> 21 (enough for +18446744073709551615)
        */
        switch(options.format)
        {
        case 'b':
        case 'B': return sizeof(T) * 8 + (options.alternate ? 2 : 0);
        case 'o': return sizeof(T) * 4 + (options.alternate ? 1 : 0);
        case 'x':
        case 'X': return sizeof(T) * 2 + (options.alternate ? 2 : 0);
        case 'p': return sizeof(T) * 2 + (options.alternate ? 1 : 0);
        case 'd':
        default: return sizeof(T) * 3 + 1 - sizeof(T) / 2;
        }
    }
    static u32 format_to(char* destination, T value, const format_options& options,
                         u32 reservedLength)
    {
        UnsignedT negative = UnsignedT(value < 0);
        u32 addSign  = u32(negative) | u32(options.sign == '+');
        char      sign     = options.sign + (('-' - options.sign) & (~negative + 1));
        UnsignedT v        = static_cast< UnsignedT >(value);
        v                  = v + ((~v + 1 - v) & (~negative + 1));

        if(options.width == 0)
        {
            switch(options.format)
            {
            case 'b':
            case 'B':
                if(options.alternate)
                {
                    destination[0]           = sign;
                    destination[0 + addSign] = '0';
                    destination[1 + addSign] = options.format;
                    return addSign + 2
                           + format_details::format_binary(destination + 2 + addSign, v, sign, 0);
                }
                else
                {
                    return format_details::format_binary(destination, v, sign, addSign);
                }
            case 'o':
                if(options.alternate)
                {
                    destination[0]           = sign;
                    destination[0 + addSign] = '0';
                    return 1 + addSign
                           + format_details::format_octal(destination + 1 + addSign, v, sign, 0);
                }
                else
                {
                    return format_details::format_octal(destination, v, sign, addSign);
                }
            case 'x':
                if(options.alternate)
                {
                    destination[0]           = sign;
                    destination[0 + addSign] = '0';
                    destination[1 + addSign] = options.format;
                    return 2 + addSign
                           + format_details::format_hexadecimal(destination + 2 + addSign, v, sign,
                                                                0, 'a');
                }
                else
                {
                    return format_details::format_hexadecimal(destination, v, sign, addSign, 'a');
                }
            case 'X':
                if(options.alternate)
                {
                    destination[0]           = sign;
                    destination[0 + addSign] = '0';
                    destination[1 + addSign] = options.format;
                    return 2 + addSign
                           + format_details::format_hexadecimal(destination + 2 + addSign, v, sign,
                                                                0, 'A');
                }
                else
                {
                    return format_details::format_hexadecimal(destination, v, sign, addSign, 'A');
                }
            case 'p':
                if(options.alternate)
                {
                    return format_details::format_hexadecimal(destination, v, '@', 1, 'A');
                }
                else
                {
                    return format_details::format_hexadecimal(destination, v, sign, addSign, 'A');
                }
            case 'd':
            default: return format_details::format_decimal(destination, v, sign, addSign);
            }
        }
        else
        {
            u32   numberSize;
            u32   alternateSize = 0;
            char* buffer        = (char*)malloca(reservedLength);

            switch(options.format)
            {
            case 'b':
            case 'B':
                numberSize    = format_details::format_binary(buffer, v, sign, 0);
                alternateSize = 2 * options.alternate;
                break;
            case 'o':
                numberSize    = format_details::format_octal(buffer, v, sign, 0);
                alternateSize = options.alternate;
                break;
            case 'x':
                numberSize    = format_details::format_hexadecimal(buffer, v, sign, 0, 'a');
                alternateSize = 2 * options.alternate;
                break;
            case 'X':
                numberSize    = format_details::format_hexadecimal(buffer, v, sign, 0, 'A');
                alternateSize = 2 * options.alternate;
                break;
            case 'p':
                numberSize    = format_details::format_hexadecimal(buffer, v, sign, 0, 'A');
                alternateSize = options.alternate;
                break;
            case 'd':
            default: numberSize = format_decimal(buffer, v, sign, 0); break;
            }

            u32 padding = (numberSize + alternateSize + addSign >= options.width)
                              ? 0
                              : (options.width - numberSize - alternateSize - addSign);
            u32 rightPadding
                = options.align == '<' ? padding : (options.align == '^' ? (padding + 1) / 2 : 0);
            u32 leftPadding = options.signPadding ? 0 : padding - rightPadding;
            u32 zeroPadding = padding - rightPadding - leftPadding;

            memset(destination, options.fill, leftPadding);
            destination += leftPadding;
            *destination = sign;
            destination += addSign & u32(options.signPadding);
            if(options.alternate)
            {
                switch(options.format)
                {
                case 'b':
                case 'B':
                case 'x':
                case 'X':
                    *destination++ = '0';
                    *destination++ = options.format;
                    break;
                case 'o': *destination++ = '0'; break;
                case 'p': *destination++ = '@'; break;
                case 'd':
                default: break;
                }
            }
            memset(destination, '0', zeroPadding);
            destination += zeroPadding;
            *destination = sign;
            destination += addSign & u32(!options.signPadding);

            memcpy(destination, buffer, numberSize);
            freea(buffer);
            memset(destination + numberSize, options.fill, rightPadding);
            return numberSize + alternateSize + addSign + padding;
        }
    }
};

}  // namespace format_details

template <>
struct formatter< const char* >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '<', ' ', 's', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 's')
            return invalid_format("string formatter does not support specified format specifier");
        return true;
    }
    static u32 length(const char* value, const format_options& options)
    {
        motor_forceuse(options);
        return u32(strlen(value));
    }
    static u32 format_to_partial(char* destination, const char* value,
                                 const format_options& options, u32 reservedLength,
                                 u32 maximalLength)
    {
        motor_forceuse(options);
        if(options.width <= reservedLength)
        {
            // string was too big for field, copy first X bytes
            memcpy(destination, value, maximalLength);
        }
        else
        {
            u32 paddingSize = options.width - reservedLength;
            u32 leftPadding = options.align == '>' ? paddingSize
                                                   : (options.align == '<' ? 0 : (paddingSize / 2));
            u32 remaining   = maximalLength;
            if(leftPadding <= remaining)
            {
                memset(destination, options.fill, leftPadding);
                remaining -= leftPadding;
                if(reservedLength <= remaining)
                {
                    memcpy(destination + leftPadding, value, reservedLength);
                    remaining -= reservedLength;
                    memset(destination + leftPadding + reservedLength, options.fill, remaining);
                }
                else
                {
                    memcpy(destination + leftPadding, value, remaining);
                }
            }
            else
            {
                memset(destination, options.fill, maximalLength);
            }
        }
        return maximalLength;
    }

    static u32 format_to(char* destination, const char* value, const format_options& options,
                         u32 reservedLength)
    {
        motor_forceuse(options);
        if(options.width <= reservedLength)
        {
            memcpy(destination, value, reservedLength);
            return reservedLength;
        }
        else
        {
            u32 paddingSize = options.width - reservedLength;
            switch(options.align)
            {
            case '<':
                memcpy(destination, value, reservedLength);
                memset(destination + reservedLength, options.fill, paddingSize);
                break;
            case '>':
                memset(destination, options.fill, paddingSize);
                memcpy(destination + paddingSize, value, reservedLength);
                break;
            case '^':
                memset(destination, options.fill, paddingSize / 2);
                memcpy(destination + paddingSize / 2, value, reservedLength);
                memset(destination + paddingSize / 2 + reservedLength, options.fill,
                       paddingSize - paddingSize / 2);
                break;
            }
            return options.width;
        }
    }
};

template <>
struct formatter< char* > : public formatter< const char* >
{
};

template <>
struct formatter< char >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '>', '-', 'c', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'c')
            return invalid_format("char formatter does not support specified format specifier");
        return true;
    }

    static constexpr u32 length(char value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 1;
    }

    static u32 format_to_partial(char* destination, char value, const format_options& options,
                                 u32 reservedLength, u32 maximalLength)
    {
        u32 paddingSize = options.width - reservedLength;
        u32 leftPadding
            = options.align == '>' ? paddingSize : (options.align == '<' ? 0 : (paddingSize / 2));
        if(leftPadding <= maximalLength)
        {
            memset(destination, options.fill, leftPadding);
            if(leftPadding < maximalLength)
            {
                destination[leftPadding] = value;
                memset(destination + leftPadding + 1, options.fill,
                       maximalLength - leftPadding - 1);
            }
        }
        else
        {
            memset(destination, options.fill, maximalLength);
        }
        return maximalLength;
    }

    static u32 format_to(char* destination, char value, const format_options& options,
                         u32 reservedLength)
    {
        if(options.width <= 1)
        {
            *destination = value;
            return 1;
        }
        else
        {
            u32 paddingSize  = options.width - reservedLength;
            u32 leftPadding  = options.align == '>' ? paddingSize
                                                    : (options.align == '<' ? 0 : (paddingSize / 2));
            u32 rightPadding = paddingSize - leftPadding;
            memset(destination, options.fill, leftPadding);
            destination[leftPadding] = value;
            memset(destination + leftPadding + 1, options.fill, rightPadding);
            return options.width;
        }
    }
};

template <>
struct formatter< bool >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '>', '-', 's', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'd' && options.format != 's')
            return invalid_format("bool formatter does not support specified format specifier");
        return true;
    }
    static constexpr u32 length(bool value, const format_options& options)
    {
        motor_forceuse(value);
        return options.format == 's' ? 5 : 1;
    }
    static u32 format_to_partial(char* destination, bool value, const format_options& options,
                                 u32 reservedLength, u32 maximalLength)
    {
        motor_forceuse(reservedLength);
        if(options.format == 's')
        {
            return formatter< const char* >::format_to_partial(
                destination, value ? "true" : "false", options, value ? 4 : 5, maximalLength);
        }
        else
        {
            return formatter< char >::format_to_partial(destination, value ? '1' : '0', options, 1,
                                                        maximalLength);
        }
    }
    static u32 format_to(char* destination, bool value, const format_options& options,
                         u32 reservedLength)
    {
        motor_forceuse(reservedLength);
        if(options.format == 's')
        {
            return formatter< const char* >::format_to(destination, value ? "true" : "false",
                                                       options, value ? 4 : 5);
        }
        else
        {
            return formatter< char >::format_to(destination, value ? '1' : '0', options, 1);
        }
    }
};

template <>
struct formatter< i8 > : public format_details::numeric_formatter< i8, u8 >
{
};

template <>
struct formatter< u8 > : public format_details::numeric_formatter< u8, u8 >
{
};

template <>
struct formatter< i16 > : public format_details::numeric_formatter< i16, u16 >
{
};

template <>
struct formatter< u16 > : public format_details::numeric_formatter< u16, u16 >
{
};

template <>
struct formatter< i32 > : public format_details::numeric_formatter< i32, u32 >
{
};

template <>
struct formatter< u32 > : public format_details::numeric_formatter< u32, u32 >
{
};

template <>
struct formatter< i64 > : public format_details::numeric_formatter< i64, u64 >
{
};

template <>
struct formatter< u64 > : public format_details::numeric_formatter< u64, u64 >
{
};

template <>
struct formatter< float > : public format_details::default_partial_formatter< float >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '>', '-', 'g', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'a' && options.format != 'A' && options.format != 'e'
           && options.format != 'E' && options.format != 'f' && options.format != 'F'
           && options.format != 'g' && options.format != 'G')
            return invalid_format(
                "floating point formatter does not support specified format specifier");
        return true;
    }
    static constexpr u32 length(float value, const format_options& options)
    {
        motor_forceuse(value);
        switch(options.format)
        {
        case 'a':
        case 'A': return 64 + (options.alternate ? 2 : 0);
        case 'e':
        case 'E': return 32 + (options.alternate ? 2 : 0);
        case 'f':
        case 'F': return 16 + (options.alternate ? 2 : 0);
        case 'g':
        case 'G': return 16 + (options.alternate ? 2 : 0);
        default: return 0;
        }
    }
    static u32 format_to(char* destination, float value, const format_options& options,
                         u32 maximalLength)
    {
        motor_forceuse(options);
        u32 result = snprintf(destination, maximalLength, "%f", value);
        return (result > maximalLength) ? maximalLength - 1 : result;
    }
};

template <>
struct formatter< double > : public format_details::default_partial_formatter< double >
{
    static constexpr format_options DefaultOptions {0, 0, ' ', '>', '-', 'g', false, false, false};
    static constexpr bool           validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'a' && options.format != 'A' && options.format != 'e'
           && options.format != 'E' && options.format != 'f' && options.format != 'F'
           && options.format != 'g' && options.format != 'G')
            return invalid_format(
                "floating point formatter does not support specified format specifier");
        return true;
    }
    static constexpr u32 length(double value, const format_options& options)
    {
        motor_forceuse(value);
        switch(options.format)
        {
        case 'a':
        case 'A': return 64 + (options.alternate ? 2 : 0);
        case 'e':
        case 'E': return 32 + (options.alternate ? 2 : 0);
        case 'f':
        case 'F': return 16 + (options.alternate ? 2 : 0);
        case 'g':
        case 'G': return 16 + (options.alternate ? 2 : 0);
        default: return 0;
        }
    }
    static u32 format_to(char* destination, double value, const format_options& options,
                         u32 maximalLength)
    {
        motor_forceuse(options);
        u32 result = snprintf(destination, maximalLength, "%f", value);
        return (result > maximalLength) ? maximalLength - 1 : result;
    }
};

template < typename T >
struct formatter< kernel::interlocked< T > > : public formatter< T >
{
};

template < typename T >
struct formatter< T* >
{
    static constexpr format_options DefaultOptions {
        0, 1 + sizeof(T*) * 2, ' ', '>', '-', 'p', false, false, true};
    static constexpr bool validate_options(const format_options& options)
    {
        using format_details::invalid_format;
        if(options.format != 'p')
            return invalid_format("pointer formatter does not support specified format specifier");
        return true;
    }
    static constexpr u32 length(const T* value, const format_options& options)
    {
        motor_forceuse(value);
#ifdef _LP64
        return 16 + (options.alternate ? 2 : 0);
#else
        return 8 + (options.alternate ? 2 : 0);
#endif
    }
    static u32 format_to_partial(char* destination, const T* value, const format_options& options,
                                 u32 reservedLength, u32 maximalLength)
    {
        union
        {
            const T* v;
            u64      v64;
            u32      v32;
        } ptrConvert;
        ptrConvert.v = value;
#ifdef _LP64
        return formatter< u64 >::format_to_partial(destination, ptrConvert.v64, options,
                                                   reservedLength, maximalLength);
#else
        return formatter< u32 >::format_to_partial(destination, ptrConvert.v32, options,
                                                   reservedLength, maximalLength);
#endif
    }
    static u32 format_to(char* destination, const T* value, const format_options& options,
                         u32 reservedLength)
    {
        union
        {
            const T* v;
            u64      v64;
            u32      v32;
        } ptrConvert;
        ptrConvert.v = value;
#ifdef _LP64
        return formatter< u64 >::format_to(destination, ptrConvert.v64, options, reservedLength);
#else
        return formatter< u32 >::format_to(destination, ptrConvert.v32, options, reservedLength);
#endif
    }
};

template < u32 SIZE >
struct formatter< format_buffer< SIZE > > : public formatter< const char* >
{
};

template < u32 SIZE >
struct formatter< char[SIZE] > : public formatter< const char* >
{
};

template < u32 SIZE >
struct formatter< const char[SIZE] > : public formatter< const char* >
{
};

}  // namespace minitl

/**************************************************************************************************/
#endif
