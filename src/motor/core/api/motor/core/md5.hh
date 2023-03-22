/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_RUNTIME_MD5_HH_
#define MOTOR_CORE_RUNTIME_MD5_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/minitl/format.hh>

namespace Motor {

struct MD5
{
    u32 hash[4];
};

static inline bool operator==(const MD5& hash1, const MD5& hash2)
{
    return hash1.hash[0] == hash2.hash[0] && hash1.hash[1] == hash2.hash[1]
           && hash1.hash[2] == hash2.hash[2] && hash1.hash[3] == hash2.hash[3];
}

motor_api(CORE) MD5 digest(const void* data, u64 size);

template < typename T >
static inline MD5 digest(const minitl::Allocator::Block< T >& block)
{
    return digest(block.data(), block.byteCount());
}

}  // namespace Motor

namespace minitl {

template <>
struct formatter< Motor::MD5 > : public format_details::default_partial_formatter< Motor::MD5 >
{
    static constexpr format_options DefaultOptions
        = {0, 0, ' ', '<', ' ', 's', false, false, false};
    static constexpr bool validate_options(const format_options& options)
    {
        if(options.format != 's')
            return format_details::invalid_format(
                "MD5 formatter does not support specified format specifier");
        return true;
    }
    static constexpr u32 length(const Motor::MD5& value, const format_options& options)
    {
        motor_forceuse(value);
        motor_forceuse(options);
        return 32;
    }
    static u32 format_to(char* destination, const Motor::MD5& value, const format_options& options,
                         u32 reservedLength)
    {
        motor_forceuse(options);
        motor_forceuse(reservedLength);
        u32 writtenLength
            = format_details::format_hexadecimal(destination, value.hash[0], ' ', 0, 'A');
        writtenLength
            += format_details::format_hexadecimal(destination, value.hash[1], ' ', 0, 'A');
        writtenLength
            += format_details::format_hexadecimal(destination, value.hash[2], ' ', 0, 'A');
        writtenLength
            += format_details::format_hexadecimal(destination, value.hash[3], ' ', 0, 'A');
        return writtenLength;
    }
};

}  // namespace minitl

/**************************************************************************************************/
#endif
