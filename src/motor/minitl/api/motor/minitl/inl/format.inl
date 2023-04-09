/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_FORMAT_INL_
#define MOTOR_MINITL_FORMAT_INL_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/minitl/format.hh>
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

/* allways allows dumping 8 bytes at once in a pattern */
static constexpr u32 g_minimumWriteSize = 8;

motor_api(MINITL) bool invalid_format(const char* reason);

struct format_pattern_info
{
    u32            start;
    u32            end;
    i32            argumentIndex;
    format_options options;
    char           formatter;
    bool           error;
};

struct brace_format
{
};

template < typename T >
struct extract_format_type;

template < char FORMAT_TYPE >
struct extract_format_type< formatter< FORMAT_TYPE > >
{
    static constexpr char format_type = FORMAT_TYPE;
};

template < typename T >
constexpr u32 count_patterns()
{
    T   format {};
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
constexpr u32 get_pattern_start(u32 patternIndex, u32 startIndex)
{
    T   format {};
    u32 result = startIndex;
    for(; format[result] != 0; ++result)
    {
        if(format[result] == '{')
        {
            if(patternIndex == 0)
            {
                return result;
            }
            ++result;
            patternIndex--;
            if(format[result] == '{') continue;
            for(; format[result] != '}' && format[result] != 0; ++result)
                /* nothing */;
        }
        else if(format[result] == '}')
        {
            if(format[result + 1] == '}')
            {
                if(patternIndex == 0)
                {
                    return result;
                }
                ++result;
                ++patternIndex;
            }
        }
    }
    return result;
}

template < typename T >
constexpr u32 get_pattern_end(u32 startIndex)
{
    T   format {};
    u32 result = startIndex + 1;
    if(format[result] == '{')
    {
        return result + 1;
    }
    for(; format[result] != 0; ++result)
    {
        if(format[result] == '}')
        {
            return result + 1;
        }
    }
    return result + (u32)invalid_format("missing closing brace '}'");
}

template < typename T >
constexpr u32 parse_integer(u32 startIndex)
{
    T   format {};
    u32 result = 0;
    for(u32 i = startIndex; format[i] >= '0' && format[i] <= '9'; ++i)
        result = result * 10 + format[i] - '0';
    return result;
}

template < typename T, u32 PATTERN_INDEX, typename... DefaultFormatters >
constexpr format_pattern_info get_format_info()
{
    T              format {};
    constexpr u32  argumentCount = sizeof...(DefaultFormatters);
    constexpr u32  patternStart  = get_pattern_start< T >(PATTERN_INDEX, 0);
    constexpr char defaultFormat[]
        = {extract_format_type< DefaultFormatters >::format_type..., '{'};
    constexpr u32  patternEnd      = get_pattern_end< T >(patternStart);
    constexpr char charAtFormatPos = format[patternEnd - 2];

    if(format[patternStart] == '}')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {patternStart + 1,
                patternEnd,
                argumentCount,
                formatter< '{' >::default_format_options,
                '{',
                !(format[patternStart + 1] == '}')
                    && invalid_format("unmatched '}' in format string")};
    }

    if(format[patternStart + 1] == '{')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {patternStart + 1,
                patternEnd,
                argumentCount,
                formatter< '{' >::default_format_options,
                '{',
                false};
    }

    u32 argumentOffset = patternStart + 1;
    if(format[argumentOffset] == '}' || format[argumentOffset] == ':')
    {
        return {patternStart,  patternEnd,
                argumentCount, formatter< 's' >::default_format_options,
                's',           invalid_format("argument index is empty")};
    }

    for(; format[argumentOffset] != '}' && format[argumentOffset] != ':'; ++argumentOffset)
    {
        if(format[argumentOffset] < '0' || format[argumentOffset] > '9')
        {
            return {patternStart,  patternEnd,
                    argumentCount, formatter< 's' >::default_format_options,
                    's',           invalid_format("argument index is not a number")};
        }
    }
    constexpr u32 argumentIndex
        = format[patternStart] == 0 ? argumentCount : parse_integer< T >(patternStart + 1);
    if(argumentIndex >= argumentCount)
    {
        return {patternStart,  patternEnd,
                argumentCount, formatter< 's' >::default_format_options,
                's',           invalid_format("argument index out of range")};
    }
    constexpr char      formatType = ((charAtFormatPos >= 'a' && charAtFormatPos <= 'z')
                                 || (charAtFormatPos >= 'A' && charAtFormatPos <= 'Z'))
                                         ? charAtFormatPos
                                         : defaultFormat[argumentIndex];
    format_pattern_info result     = {patternStart,  argumentOffset,
                                      argumentIndex, formatter< formatType >::default_format_options,
                                      formatType,    false};

    if(format[result.end++] == '}')
    {
        return result;
    }
    if(format[result.end] == '<' || format[result.end] == '>' || format[result.end] == '^')
    {
        result.options.align = format[result.end];
        result.end++;
    }
    else if(format[result.end + 1] == '<' || format[result.end + 1] == '>'
            || format[result.end + 1] == '^')
    {
        result.options.fill = format[result.end];
        result.end++;
        result.options.align = format[result.end];
        result.end++;
    }
    if(format[result.end] == ' ' || format[result.end] == '-' || format[result.end] == '+')
    {
        result.options.sign = format[result.end];
        result.end++;
    }
    if(format[result.end] == '#')
    {
        result.options.alternate = true;
        result.end++;
    }
    if(format[result.end] == '0')
    {
        result.options.signPadding = true;
        result.end++;
    }
    if(format[result.end] > '0' && format[result.end] <= '9')
    {
        result.options.width = 0;
        for(; format[result.end] >= '0' && format[result.end] <= '9'; result.end++)
            result.options.width = result.options.width * 10 + format[result.end] - '0';
    }
    if(format[result.end] == '.')
    {
        result.options.precision = 0;
        result.end++;
        for(; format[result.end] >= '0' && format[result.end] <= '9'; result.end++)
            result.options.width = result.options.width * 10 + format[result.end] - '0';
    }
    if(format[result.end] != '}')
    {
        result.end++;
    }
    if(format[result.end++] != '}')
    {
        result.error = invalid_format("invalid format options");
    }
    return result;
}

template < typename T, u32 PATTERN_INDEX >
constexpr format_pattern_info get_format_info_end()
{
    T format {};
    return {format.size(), format.size(), PATTERN_INDEX, formatter< '{' >::default_format_options,
            '{',           false};
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

struct buffer_info
{
    u32 pattern_offset;
    u32 destination_offset;
};

template < typename T, typename Formatter, typename Arg >
buffer_info fill_buffer(char* destination, u32 length, const buffer_info& bufferInfo,
                        const format_pattern_info& patternInfo, u32 argumentLength,
                        const Formatter& formatter, const Arg& arg)
{
    T   format;
    u32 offset        = bufferInfo.destination_offset;
    u32 maxSize       = length - offset;
    u32 segmentLength = patternInfo.start - bufferInfo.pattern_offset;
    if(segmentLength <= maxSize)
    {
        memcpy(destination + offset, &format[bufferInfo.pattern_offset], segmentLength);
        offset += segmentLength;
        maxSize -= segmentLength;
    }
    else
    {
        memcpy(destination + offset, &format[bufferInfo.pattern_offset], maxSize - 3);
        return {patternInfo.end, offset + maxSize};
    }
    if(argumentLength <= maxSize)
    {
        offset += formatter.write(destination + offset, arg, patternInfo.options, argumentLength);
    }
    else if(maxSize > 0)
    {
        offset += formatter.write_partial(destination + offset, arg, patternInfo.options,
                                          argumentLength, maxSize);
    }
    return {patternInfo.end, offset};
}

template < typename T >
buffer_info fill_buffer(char* destination, u32 length, const buffer_info& bufferInfo,
                        const format_pattern_info& patternInfo, u32 argumentLength,
                        const formatter< '{' >&, const brace_format&)
{
    motor_forceuse(argumentLength);
    T   format;
    u32 offset        = bufferInfo.destination_offset;
    u32 maxSize       = length - offset;
    u32 segmentLength = patternInfo.start - bufferInfo.pattern_offset;
    if(segmentLength <= maxSize)
    {
        memcpy(destination + offset, &format[bufferInfo.pattern_offset], segmentLength);
        offset += segmentLength;
    }
    else
    {
        memcpy(destination + offset, &format[bufferInfo.pattern_offset], maxSize - 3);
        return {patternInfo.end, offset + maxSize};
    }
    return {patternInfo.end, offset};
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
u32 format(char* destination, u32 destinationLength, Args&&... arguments,
           index_sequence< PATTERN_INDICES... >, index_sequence< ARGUMENT_INDICES... >)
{
    T                             format;
    constexpr u32                 patternCount = sizeof...(PATTERN_INDICES);
    constexpr format_pattern_info patterns[patternCount + 1]
        = {get_format_info< T, PATTERN_INDICES,
                            decltype(format_as(minitl::forward< Args >(arguments)))... >()...,
           get_format_info_end< T, sizeof...(PATTERN_INDICES) >()};
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
            typename alternate_formatter< formatter< patterns[PATTERN_INDICES].formatter >,
                                          patterns[PATTERN_INDICES].options.alternate >::type,
            alignments[PATTERN_INDICES] >::type()...);

    u32 lengths[patternCount] = {
        get< PATTERN_INDICES >(formatters)
            .length(get< patterns[PATTERN_INDICES].argumentIndex >(arguments..., brace_format {}),
                    patterns[PATTERN_INDICES].options)...};

    u32 length = 0, p = 0;
    for(u32 i = 0; i < patternCount; ++i)
    {
        length += patterns[i].start - p;
        length += (lengths[i] < patterns[i].options.width) ? patterns[i].options.width : lengths[i];
        p = patterns[i].end;
    }
    if(patternCount >= 1
       && patterns[patternCount].start - patterns[patternCount - 1].start < g_minimumWriteSize)
        length += g_minimumWriteSize;
    else
        length += patterns[patternCount].start - p;

    buffer_info bi {0, 0};
    buffer_info bis[]
        = {bi = fill_buffer< T >(
               destination, destinationLength, bi, patterns[PATTERN_INDICES],
               lengths[PATTERN_INDICES], get< patterns[PATTERN_INDICES].argumentIndex >(formatters),
               get< patterns[PATTERN_INDICES].argumentIndex >(arguments..., brace_format {}))...};
    motor_forceuse(bis);

    u32 offset        = bi.destination_offset;
    u32 maxSize       = length - offset;
    u32 segmentLength = patterns[patternCount].start - bi.pattern_offset;
    segmentLength     = (segmentLength > maxSize) ? maxSize : segmentLength;
    memcpy(destination + offset, &format[bi.pattern_offset], segmentLength);
    offset += segmentLength;
    if(offset < destinationLength)
    {
        destination[offset] = '\0';
        return offset;
    }
    else
    {
        destination[length - 4]            = '.';
        destination[destinationLength - 3] = '.';
        destination[destinationLength - 2] = '.';
        destination[destinationLength - 1] = '\0';
        return destinationLength - 1;
    }
}

formatter< '{' > format_as(format_details::brace_format);

}  // namespace format_details

template < u32 SIZE = 1024, typename T, typename... Args >
format_buffer< SIZE > format(T format, Args&&... arguments)
{
    format_buffer< SIZE > result;
    motor_forceuse(format);

    format_details::format< T, Args... >(
        result.buffer, SIZE, minitl::forward< Args >(arguments)...,
        make_index_sequence< format_details::count_patterns< T >() >(),
        make_index_sequence< sizeof...(Args) >());
    return result;
}

template < typename T, typename... Args >
u32 format_to(char* destination, u32 length, T format, Args&&... arguments)
{
    motor_forceuse(format);
    return format_details::format< T, Args... >(
        destination, length, minitl::forward< Args >(arguments)...,
        make_index_sequence< format_details::count_patterns< T >() >(),
        make_index_sequence< sizeof...(Args) >());
}

}  // namespace minitl

/**************************************************************************************************/
#endif
