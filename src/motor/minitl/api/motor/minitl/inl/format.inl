/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_FORMAT_INL_
#define MOTOR_MINITL_FORMAT_INL_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <motor/minitl/assert.hh>
#include <motor/minitl/format.hh>
#include <motor/minitl/utility.hh>

namespace minitl {

namespace format_details {

/* allways allows dumping 8 bytes at once in a pattern */
static constexpr u32 g_minimumWriteSize = 8;

motor_api(MINITL) bool invalid_format(const char* reason);

struct format_pattern_info
{
    u32            start;
    u32            end;
    i32            argumentIndex;
    format_options options;
    bool           error;
};

template < u32 COUNT >
struct format_pattern_infos
{
    format_pattern_info info[COUNT];
};

template < u32 COUNT >
struct format_pattern_lengths
{
    u32 length[COUNT];
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

template < typename T, typename... Args >
constexpr format_pattern_info get_format_info(u32 patternIndex, u32 patternStart)
{
    T format {};
    typedef bool (*option_checker)(const format_options&);
    constexpr format_options defaultOptions[] {formatter< Args >::DefaultOptions...};
    constexpr option_checker optionCheckers[] {&formatter< Args >::validate_options...};
    constexpr u32            argumentCount = sizeof...(Args);
    patternStart                           = get_pattern_start< T >(patternIndex, patternStart);

    format_pattern_info result = {patternStart, patternStart, 0, {}, false};
    if(format[patternStart] == 0)
    {
        return result;
    }

    ++result.end;
    if(format[result.start] == '}')
    {
        result.start++;
        if(format[result.end++] != '}')
        {
            result.error = invalid_format("unmatched '}' in format string");
        }
        result.argumentIndex = -1;
        return result;
    }

    if(format[result.end] == '{')
    {
        result.start++;
        result.end++;
        result.argumentIndex = -1;
        return result;
    }
    if(format[result.end] == '}' || format[result.end] == ':')
    {
        result.error = invalid_format("argument index is empty");
        return result;
    }
    for(; format[result.end] != '}' && format[result.end] != ':'; ++result.end)
    {
        if(format[result.end] < '0' || format[result.end] > '9')
        {
            result.error = invalid_format("argument index is not a number");
            return result;
        }
        result.argumentIndex = result.argumentIndex * 10 + format[result.end] - '0';
    }
    if(result.argumentIndex >= argumentCount)
    {
        result.error = invalid_format("argument index out of range");
        return result;
    }

    result.options = defaultOptions[result.argumentIndex];
    if(format[result.end] != ':' && format[result.end] != '}')
    {
        result.error = invalid_format("expected ':' or '}' after argument index");
        return result;
    }
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
        result.options.format = format[result.end];
        result.end++;
    }
    if(format[result.end++] != '}')
    {
        result.error = invalid_format("invalid format options");
    }
    result.error = optionCheckers[result.argumentIndex](result.options);
    return result;
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

template < typename T, i32 ARG_INDEX, typename... Args,
           enable_if_t< (ARG_INDEX >= 0), int > = true >
buffer_info fill_buffer(char* destination, u32 length, const buffer_info& bufferInfo,
                        const format_pattern_info& patternInfo, u32 argumentLength,
                        const Args&... arguments)
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
        offset += formatter< decltype(get< ARG_INDEX >(arguments...)) >::format_to(
            destination + offset, get< ARG_INDEX >(arguments...), patternInfo.options,
            argumentLength);
    }
    else if(maxSize > 0)
    {
        offset += formatter< decltype(get< ARG_INDEX >(arguments...)) >::format_to_partial(
            destination + offset, get< ARG_INDEX >(arguments...), patternInfo.options,
            argumentLength, maxSize);
    }
    return {patternInfo.end, offset};
}

template < typename T, i32 ARG_INDEX, typename... Args,
           enable_if_t< (ARG_INDEX < 0), bool > = true >
buffer_info fill_buffer(char* destination, u32 length, const buffer_info& bufferInfo,
                        const format_pattern_info& patternInfo, u32 argumentLength,
                        const Args&... arguments)
{
    motor_forceuse(argumentLength);
    motor_forceuse_pack(arguments);
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
    return {patternInfo.end, offset};
}

template < typename T, typename... Args, u32... PATTERN_INDICES, u32... ARGUMENT_INDICES >
u32 format(char* destination, u32 destinationLength, const Args&... arguments,
              index_sequence< PATTERN_INDICES... >, index_sequence< ARGUMENT_INDICES... >)
{
    T                             format;
    constexpr u32                 patternCount = sizeof...(PATTERN_INDICES);
    constexpr format_pattern_info patterns[patternCount + 1]
        = {get_format_info< T, Args... >(PATTERN_INDICES, 0)...,
           get_format_info< T, Args... >(sizeof...(PATTERN_INDICES), 0)};
    constexpr bool argUsed[]
        = {isIndexInList< ARGUMENT_INDICES, patterns[PATTERN_INDICES].argumentIndex... >()...};
    motor_forceuse(argUsed);
    u32 lengths[patternCount]
        = {patterns[PATTERN_INDICES].argumentIndex == -1
               ? 0
               : formatter< decltype(get< patterns[PATTERN_INDICES].argumentIndex + 1 >(
                   0, arguments...)) >::length(get< patterns[PATTERN_INDICES].argumentIndex
                                                    + 1 >(0, arguments...),
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
    p = 0;

    buffer_info bi {0, 0};
    buffer_info bis[] = {bi = fill_buffer< T, patterns[PATTERN_INDICES].argumentIndex >(
                             destination, destinationLength, bi, patterns[PATTERN_INDICES],
                             lengths[PATTERN_INDICES], arguments...)...};
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

}  // namespace format_details

template < u32 SIZE, typename T, typename... Args >
format_buffer< SIZE > format(const T format, Args&&... arguments)
{
    format_buffer< SIZE > result;
    motor_forceuse(format);

    format_details::format< T, Args... >(
        result.buffer, SIZE, arguments...,
        make_index_sequence< format_details::count_patterns< T >() >(),
        make_index_sequence< sizeof...(Args) >());
    return result;
}

template < typename T, typename... Args >
u32 format_to(char* destination, u32 length, const T format, Args&&... arguments)
{
    motor_forceuse(format);
    return format_details::format< T, Args... >(
        destination, length, arguments...,
        make_index_sequence< format_details::count_patterns< T >() >(),
        make_index_sequence< sizeof...(Args) >());
}

}  // namespace minitl

/**************************************************************************************************/
#endif
