/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    u32            block_start;
    u32            pattern_start;
    u32            pattern_end;
    u32            argument_index;
    format_options options;
    bool           error;
};

struct brace_format
{
};

struct pattern_range
{
    u32 block_start;
    u32 pattern_start;
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
constexpr pattern_range get_pattern_start(u32 pattern_index, u32 start_index)
{
    T   format {};
    u32 first  = start_index;
    u32 result = start_index;
    for(; format[result] != 0; ++result)
    {
        if(format[result] == '{')
        {
            if(pattern_index == 0)
            {
                return {first, result};
            }
            ++result;
            pattern_index--;
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
                if(pattern_index == 0)
                {
                    return {first, result};
                }
                ++result;
                pattern_index--;
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
    result.pattern_end = offset + 1;
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
        result.options.sign_padding = true;
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

template < typename T, u32 PATTERN_INDEX, typename... DEFAULT_FORMATTERS >
constexpr format_pattern_info get_format_info(T format)
{
    constexpr u32            argument_count = sizeof...(DEFAULT_FORMATTERS);
    constexpr format_options default_format[argument_count]
        = {DEFAULT_FORMATTERS::default_format_options...};
    pattern_range range         = get_pattern_start< T >(PATTERN_INDEX, 0);
    u32           pattern_start = range.pattern_start;

    if(format[pattern_start] == '}')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {range.block_start,
                pattern_start + 1,
                pattern_start + 2,
                argument_count,
                formatter< '{' >::default_format_options,
                !(format[pattern_start + 1] == '}')
                    && invalid_format("unmatched '}' in format string")};
    }

    if(format[pattern_start + 1] == '{')
    {
        // deliberate offset to include the '{}' characters in the copy
        return {range.block_start,
                pattern_start + 1,
                pattern_start + 2,
                argument_count,
                formatter< '{' >::default_format_options,
                false};
    }

    u32 argument_offset = pattern_start + 1;
    if(format[argument_offset] == '}' || format[argument_offset] == ':')
    {
        return {range.block_start,
                pattern_start,
                pattern_start + 1,
                argument_count,
                formatter< 's' >::default_format_options,
                invalid_format("argument index is empty")};
    }

    u32 argument_index = 0;
    for(; format[argument_offset] != '}' && format[argument_offset] != ':'; ++argument_offset)
    {
        if(format[argument_offset] < '0' || format[argument_offset] > '9')
        {
            return {range.block_start,
                    pattern_start,
                    pattern_start + 1,
                    argument_count,
                    formatter< 's' >::default_format_options,
                    invalid_format("argument index is not a number")};
        }
        argument_index = argument_index * 10 + format[argument_offset] - '0';
    }

    if(argument_index >= argument_count)
    {
        return {range.block_start,
                pattern_start,
                pattern_start + 1,
                argument_count,
                formatter< 's' >::default_format_options,
                invalid_format("argument index out of range")};
    }
    format_pattern_info result = {range.block_start,
                                  pattern_start,
                                  argument_offset + 1,
                                  argument_index,
                                  default_format[argument_index],
                                  false};
    if(format[argument_offset] == ':')
    {
        fill_format_info_align(format, argument_offset + 1, result);
    }
    return result;
}

template < typename T, u32 PATTERN_INDEX >
constexpr format_pattern_info get_format_info_end(T format, u32 block_start)
{
    return {block_start,
            format.size(),
            format.size(),
            PATTERN_INDEX,
            formatter< '{' >::default_format_options,
            false};
}

template < u32 INDEX >
constexpr bool is_index_in_list()
{
    return invalid_format("argument not used in format");
}

template < u32 INDEX, i32 FIRST, i32... INDICES, enable_if_t< INDEX == FIRST, bool > = true >
constexpr bool is_index_in_list()
{
    return true;
}

template < u32 INDEX, i32 FIRST, i32... INDICES, enable_if_t< INDEX != FIRST, int > = true >
constexpr bool is_index_in_list()
{
    return is_index_in_list< INDEX, INDICES... >();
}

template < typename T, typename FORMATTER, typename ARG >
u32 fill_buffer(char* destination, u32 length, u32 offset, const format_pattern_info& pattern_info,
                u32 argument_length, const FORMATTER& formatter, ARG&& arg)
{
    T   format;
    u32 max_size       = length - offset;
    u32 segment_length = pattern_info.pattern_start - pattern_info.block_start;
    segment_length     = segment_length > max_size ? max_size : segment_length;
    memcpy(destination + offset, &format[pattern_info.block_start], segment_length);
    offset += segment_length;
    max_size -= segment_length;
    if(argument_length <= max_size)
    {
        offset += formatter.write(destination + offset, minitl::forward< ARG >(arg),
                                  pattern_info.options, argument_length);
    }
    else if(max_size > 0)
    {
        offset += formatter.write_partial(destination + offset, minitl::forward< ARG >(arg),
                                          pattern_info.options, argument_length, max_size);
    }
    return offset;
}

template < typename T >
u32 fill_buffer(char* destination, u32 length, u32 offset, const format_pattern_info& pattern_info,
                u32 argument_length, const formatter< '{' >&, const brace_format&)
{
    motor_forceuse(argument_length);
    T   format;
    u32 max_size       = length - offset;
    u32 segment_length = pattern_info.pattern_start - pattern_info.block_start;
    segment_length     = segment_length > max_size ? max_size : segment_length;
    memcpy(destination + offset, &format[pattern_info.block_start], segment_length);
    return offset + segment_length;
}

enum struct format_alignment
{
    none,
    left,
    right,
    center
};

template < typename FORMATTER, format_alignment >
struct aligned_formatter;

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::none >
{
    typedef FORMATTER formatter_t;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::left >
{
    typedef typename FORMATTER::formatter_left_aligned formatter_t;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::right >
{
    typedef typename FORMATTER::formatter_right_aligned formatter_t;
};

template < typename FORMATTER >
struct aligned_formatter< FORMATTER, format_alignment::center >
{
    typedef typename FORMATTER::formatter_centered formatter_t;
};

template < typename FORMATTER, format_alignment ALIGNMENT >
using aligned_formatter_t = typename aligned_formatter< FORMATTER, ALIGNMENT >::formatter_t;

template < typename FORMATTER, bool >
struct alternate_formatter;

template < typename FORMATTER >
struct alternate_formatter< FORMATTER, false >
{
    typedef FORMATTER formatter_t;
};

template < typename FORMATTER >
struct alternate_formatter< FORMATTER, true >
{
    typedef typename FORMATTER::formatter_alternate formatter_t;
};

template < typename FORMATTER, bool USE_ALTERNATE >
using alternate_formatter_t = typename alternate_formatter< FORMATTER, USE_ALTERNATE >::formatter_t;

template < typename T, typename... ARGS, u32... PATTERN_INDICES, u32... ARGUMENT_INDICES >
u32 format(char* destination, u32 destination_length, index_sequence< PATTERN_INDICES... >,
           index_sequence< ARGUMENT_INDICES... >, ARGS&&... arguments)
{
    constexpr T                   format {};
    constexpr u32                 pattern_count           = sizeof...(PATTERN_INDICES);
    constexpr format_pattern_info patterns[pattern_count] = {
        get_format_info< T, PATTERN_INDICES,
                         decltype(format_as(minitl::forward< ARGS >(arguments)))... >(format)...};
    constexpr bool arg_used[]
        = {is_index_in_list< ARGUMENT_INDICES, u32(sizeof...(ARGS)),
                             patterns[PATTERN_INDICES].argument_index... >()...};
    motor_forceuse(arg_used);  // no check needed here
    constexpr format_alignment alignments[]
        = {patterns[PATTERN_INDICES].options.width == 0
               ? format_alignment::none
               : (patterns[PATTERN_INDICES].options.align == '<'
                      ? format_alignment::left
                      : (patterns[PATTERN_INDICES].options.align == '>'
                             ? format_alignment::right
                             : format_alignment::center))...};
    constexpr auto formatters = make_tuple(
        aligned_formatter_t<
            alternate_formatter_t< formatter< patterns[PATTERN_INDICES].options.formatter >,
                                   patterns[PATTERN_INDICES].options.alternate >,
            alignments[PATTERN_INDICES] >()...);

    u32 lengths[pattern_count] = {
        get< PATTERN_INDICES >(formatters)
            .length(get< patterns[PATTERN_INDICES].argument_index >(arguments..., brace_format {}),
                    patterns[PATTERN_INDICES].options)...};

    u32 offset    = 0;
    u32 offsets[] = {
        offset = fill_buffer< T >(
            destination, destination_length, offset, patterns[PATTERN_INDICES],
            lengths[PATTERN_INDICES], get< patterns[PATTERN_INDICES].argument_index >(formatters),
            get< patterns[PATTERN_INDICES].argument_index >(arguments..., brace_format {}))...};
    motor_forceuse(offsets);

    u32 max_size       = destination_length - offset;
    u32 segment_length = format.size() - patterns[pattern_count - 1].pattern_end;
    segment_length     = (segment_length > max_size) ? max_size : segment_length;
    memcpy(destination + offset, &format[patterns[pattern_count - 1].pattern_end], segment_length);
    offset += segment_length;
    if(offset < destination_length)
    {
        return offset - 1;
    }
    else
    {
        destination[destination_length - 4] = '.';
        destination[destination_length - 3] = '.';
        destination[destination_length - 2] = '.';
        destination[destination_length - 1] = '\0';
        return destination_length - 1;
    }
}

formatter< '{' > format_as(format_details::brace_format);

}  // namespace format_details

template < u32 SIZE, typename T, typename... ARGS >
format_buffer< SIZE > format(T format_string, ARGS&&... arguments)
{
    format_buffer< SIZE > result;
    format_to(result.buffer, SIZE, format_string, minitl::forward< ARGS >(arguments)...);
    return result;
}

template < typename T, typename... ARGS >
u32 format_to(char* destination, u32 length, T format_string, ARGS&&... arguments)
{
    motor_forceuse(format_string);
    constexpr u32 pattern_count = format_details::count_patterns(T {});

    return format_details::format< T >(destination, length, make_index_sequence< pattern_count >(),
                                       make_index_sequence< sizeof...(ARGS) >(),
                                       minitl::forward< ARGS >(arguments)...);
}

}  // namespace minitl
