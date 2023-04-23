/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_FORMAT_INL_
#define MOTOR_MINITL_FORMAT_INL_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/tuple.hh>
#include <motor/minitl/utility.hh>

#include <motor/minitl/inl/formatter.inl>

namespace minitl {

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
    u32            blockStart;
    u32            patternStart;
    u32            patternEnd;
    u32            argumentIndex;
    format_options options;
    bool           error;
};

struct brace_format
{
};

struct pattern_range
{
    u32 blockStart;
    u32 patternStart;
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
constexpr pattern_range get_pattern_start(u32 patternIndex, u32 startIndex)
{
    T   format {};
    u32 first  = startIndex;
    u32 result = startIndex;
    for(; format[result] != 0; ++result)
    {
        if(format[result] == '{')
        {
            if(patternIndex == 0)
            {
                return {first, result};
            }
            ++result;
            patternIndex--;
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
                if(patternIndex == 0)
                {
                    return {first, result};
                }
                ++result;
                patternIndex--;
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
    // case 'b': result.options = formatter< 'b' >::default_format_options; break;
    // case 'B': result.options = formatter< 'B' >::default_format_options; break;
    // case 'o': result.options = formatter< 'o' >::default_format_options; break;
    case 'x': result.options = formatter< 'x' >::default_format_options; break;
    // case 'X': result.options = formatter< 'X' >::default_format_options; break;
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
    result.patternEnd = offset + 1;
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
constexpr void fill_format_info_signaware(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] == '0')
    {
        fill_format_info_width(format, offset + 1, result);
        result.options.signPadding = true;
    }
    else
    {
        fill_format_info_width(format, offset, result);
    }
}

template < typename T >
constexpr void fill_format_info_alternate(T format, u32 offset, format_pattern_info& result)
{
    if(format[offset] == '#')
    {
        fill_format_info_signaware(format, offset + 1, result);
        result.options.alternate = true;
    }
    else
    {
        fill_format_info_signaware(format, offset, result);
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

template < typename T, u32 PATTERN_INDEX, typename... DefaultFormatters >
constexpr format_pattern_info get_format_info(T format)
{
    constexpr u32            argumentCount = sizeof...(DefaultFormatters);
    constexpr format_options defaultFormat[argumentCount]
        = {DefaultFormatters::default_format_options...};
    pattern_range range        = get_pattern_start< T >(PATTERN_INDEX, 0);
    u32           patternStart = range.patternStart;

    if(format[patternStart] == '}')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {range.blockStart,
                patternStart + 1,
                patternStart + 2,
                argumentCount,
                formatter< '{' >::default_format_options,
                !(format[patternStart + 1] == '}')
                    && invalid_format("unmatched '}' in format string")};
    }

    if(format[patternStart + 1] == '{')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {range.blockStart,
                patternStart + 1,
                patternStart + 2,
                argumentCount,
                formatter< '{' >::default_format_options,
                false};
    }

    u32 argumentOffset = patternStart + 1;
    if(format[argumentOffset] == '}' || format[argumentOffset] == ':')
    {
        return {range.blockStart,
                patternStart,
                patternStart + 1,
                argumentCount,
                formatter< 's' >::default_format_options,
                invalid_format("argument index is empty")};
    }

    u32 argumentIndex = 0;
    for(; format[argumentOffset] != '}' && format[argumentOffset] != ':'; ++argumentOffset)
    {
        if(format[argumentOffset] < '0' || format[argumentOffset] > '9')
        {
            return {range.blockStart,
                    patternStart,
                    patternStart + 1,
                    argumentCount,
                    formatter< 's' >::default_format_options,
                    invalid_format("argument index is not a number")};
        }
        argumentIndex = argumentIndex * 10 + format[argumentOffset] - '0';
    }

    if(argumentIndex >= argumentCount)
    {
        return {range.blockStart,
                patternStart,
                patternStart + 1,
                argumentCount,
                formatter< 's' >::default_format_options,
                invalid_format("argument index out of range")};
    }
    format_pattern_info result = {range.blockStart,
                                  patternStart,
                                  argumentOffset + 1,
                                  argumentIndex,
                                  defaultFormat[argumentIndex],
                                  false};
    if(format[argumentOffset] == ':')
    {
        fill_format_info_align(format, argumentOffset + 1, result);
    }
    return result;
}

template < typename T, u32 PATTERN_INDEX >
constexpr format_pattern_info get_format_info_end(T format, u32 blockStart)
{
    return {blockStart,
            format.size(),
            format.size(),
            PATTERN_INDEX,
            formatter< '{' >::default_format_options,
            false};
}

template < u32 INDEX >
constexpr bool isIndexInList()
{
    return invalid_format("argument not used in format");
}

template < u32 INDEX, i32 FIRST, i32... INDICES, enable_if_t< INDEX == FIRST, bool > = true >
constexpr bool isIndexInList()
{
    return true;
}

template < u32 INDEX, i32 FIRST, i32... INDICES, enable_if_t< INDEX != FIRST, int > = true >
constexpr bool isIndexInList()
{
    return isIndexInList< INDEX, INDICES... >();
}

template < typename T, typename Formatter, typename Arg >
u32 fill_buffer(char* destination, u32 length, u32 offset, const format_pattern_info& patternInfo,
                u32 argumentLength, const Formatter& formatter, Arg&& arg)
{
    T   format;
    u32 maxSize       = length - offset;
    u32 segmentLength = patternInfo.patternStart - patternInfo.blockStart;
    segmentLength     = segmentLength > maxSize ? maxSize : segmentLength;
    memcpy(destination + offset, &format[patternInfo.blockStart], segmentLength);
    offset += segmentLength;
    maxSize -= segmentLength;
    if(argumentLength <= maxSize)
    {
        offset += formatter.write(destination + offset, minitl::forward< Arg >(arg),
                                  patternInfo.options, argumentLength);
    }
    else if(maxSize > 0)
    {
        offset += formatter.write_partial(destination + offset, minitl::forward< Arg >(arg),
                                          patternInfo.options, argumentLength, maxSize);
    }
    return offset;
}

template < typename T >
u32 fill_buffer(char* destination, u32 length, u32 offset, const format_pattern_info& patternInfo,
                u32 argumentLength, const formatter< '{' >&, const brace_format&)
{
    motor_forceuse(argumentLength);
    T   format;
    u32 maxSize       = length - offset;
    u32 segmentLength = patternInfo.patternStart - patternInfo.blockStart;
    segmentLength     = segmentLength > maxSize ? maxSize : segmentLength;
    memcpy(destination + offset, &format[patternInfo.blockStart], segmentLength);
    return offset + segmentLength;
}

enum struct format_alignment
{
    None,
    Left,
    Right,
    Center
};

template < typename FORMATTER, format_alignment >
struct aligned_formatter;

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::None >
{
    typedef FORMATTER type;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::Left >
{
    typedef typename FORMATTER::formatter_left_aligned type;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::Right >
{
    typedef typename FORMATTER::formatter_right_aligned type;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::Center >
{
    typedef typename FORMATTER::formatter_centered type;
};

template < typename FORMATTER, bool >
struct alternate_formatter;

template < typename FORMATTER >
struct alternate_formatter< FORMATTER, false >
{
    typedef FORMATTER type;
};

template < typename FORMATTER >
struct alternate_formatter< FORMATTER, true >
{
    typedef typename FORMATTER::formatter_alternate type;
};

template < typename T, typename... Args, u32... PATTERN_INDICES, u32... ARGUMENT_INDICES >
u32 format(char* destination, u32 destinationLength, index_sequence< PATTERN_INDICES... >,
           index_sequence< ARGUMENT_INDICES... >, Args&&... arguments)
{
    constexpr T                   format {};
    constexpr u32                 patternCount           = sizeof...(PATTERN_INDICES);
    constexpr format_pattern_info patterns[patternCount] = {
        get_format_info< T, PATTERN_INDICES,
                         decltype(format_as(minitl::forward< Args >(arguments)))... >(format)...};
    constexpr bool argUsed[] = {isIndexInList< ARGUMENT_INDICES, u32(sizeof...(Args)),
                                               patterns[PATTERN_INDICES].argumentIndex... >()...};
    motor_forceuse(argUsed);  // no check needed here
    constexpr format_alignment alignments[]
        = {patterns[PATTERN_INDICES].options.width == 0
               ? format_alignment::None
               : (patterns[PATTERN_INDICES].options.align == '<'
                      ? format_alignment::Left
                      : (patterns[PATTERN_INDICES].options.align == '>'
                             ? format_alignment::Right
                             : format_alignment::Center))...};
    constexpr auto formatters = make_tuple(
        typename aligned_formatter<
            typename alternate_formatter< formatter< patterns[PATTERN_INDICES].options.formatter >,
                                          patterns[PATTERN_INDICES].options.alternate >::type,
            alignments[PATTERN_INDICES] >::type()...);

    u32 lengths[patternCount] = {
        get< PATTERN_INDICES >(formatters)
            .length(get< patterns[PATTERN_INDICES].argumentIndex >(arguments..., brace_format {}),
                    patterns[PATTERN_INDICES].options)...};

    u32 offset = 0;
    u32 offsets[]
        = {offset = fill_buffer< T >(
               destination, destinationLength, offset, patterns[PATTERN_INDICES],
               lengths[PATTERN_INDICES], get< patterns[PATTERN_INDICES].argumentIndex >(formatters),
               get< patterns[PATTERN_INDICES].argumentIndex >(arguments..., brace_format {}))...};
    motor_forceuse(offsets);

    u32 maxSize       = destinationLength - offset;
    u32 segmentLength = format.size() - patterns[patternCount - 1].patternEnd;
    segmentLength     = (segmentLength > maxSize) ? maxSize : segmentLength;
    memcpy(destination + offset, &format[patterns[patternCount - 1].patternEnd], segmentLength);
    offset += segmentLength;
    if(offset < destinationLength)
    {
        return offset - 1;
    }
    else
    {
        destination[destinationLength - 4] = '.';
        destination[destinationLength - 3] = '.';
        destination[destinationLength - 2] = '.';
        destination[destinationLength - 1] = '\0';
        return destinationLength - 1;
    }
}

formatter< '{' > format_as(format_details::brace_format);

}  // namespace format_details

template < u32 SIZE, typename T, typename... Args >
format_buffer< SIZE > format(T formatString, Args&&... arguments)
{
    format_buffer< SIZE > result;
    format_to(result.buffer, SIZE, formatString, minitl::forward< Args >(arguments)...);
    return result;
}

template < typename T, typename... Args >
u32 format_to(char* destination, u32 length, T format, Args&&... arguments)
{
    motor_forceuse(format);
    constexpr u32 patternCount = format_details::count_patterns(T {});

    return format_details::format< T >(destination, length, make_index_sequence< patternCount >(),
                                       make_index_sequence< sizeof...(Args) >(),
                                       minitl::forward< Args >(arguments)...);
}

}  // namespace minitl

/**************************************************************************************************/
#endif
