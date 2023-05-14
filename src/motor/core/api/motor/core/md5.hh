/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>
#include <motor/minitl/format.hh>

namespace Motor {

struct MD5
{
    u32 hash[4] {};
};

static inline bool operator==(const MD5& hash1, const MD5& hash2)
{
    return hash1.hash[0] == hash2.hash[0] && hash1.hash[1] == hash2.hash[1]
           && hash1.hash[2] == hash2.hash[2] && hash1.hash[3] == hash2.hash[3];
}

motor_api(CORE) MD5 digest(const void* data, u64 size);

template < typename T >
static inline MD5 digest(const minitl::allocator::block< T >& block)
{
    return digest(block.data(), block.byte_count());
}

motor_api(CORE) u32 format_length(const MD5& md5, const minitl::format_options& options);
motor_api(CORE) u32 format_arg(char* destination, const MD5& md5,
                               const minitl::format_options& options, u32 reservedLength);
motor_api(CORE) u32
    format_arg_partial(char* destination, const MD5& md5, const minitl::format_options& options,
                       u32 reservedLength, u32 maxCapacity);

}  // namespace Motor
