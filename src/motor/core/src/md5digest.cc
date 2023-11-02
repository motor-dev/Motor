/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/md5.hh>

extern "C"
{
#include <md5/md5.h>
}

namespace Motor {

MD5 digest(const void* data, u64 size)
{
    MD5_CTX context;
    MD5Init(&context);
    MD5Update(&context, (unsigned char*)data, motor_checked_numcast< unsigned int >(size));
    MD5Final(&context);
    MD5 result = {{0, 0, 0, 0}};

    for(int i = 0; i < 4; ++i)
        result.hash[i] = context.digest[i * 4 + 0] << 0 | context.digest[i * 4 + 1] << 8
                         | context.digest[i * 4 + 2] << 16 | context.digest[i * 4 + 3] << 24;
    return result;
}

u32 format_length(const MD5& md5, const minitl::format_options& options)
{
    motor_forceuse(md5);
    motor_forceuse(options);
    return 32;
}

u32 format_arg(char* destination, const MD5& md5, const minitl::format_options& options,
               u32 reservedLength)
{
    motor_forceuse(options);
    motor_forceuse(reservedLength);
    using minitl::format_details::hexadecimal_format::format_hexadecimal_whole;
    destination += format_hexadecimal_whole(destination, md5.hash[0]);
    destination += format_hexadecimal_whole(destination, md5.hash[1]);
    destination += format_hexadecimal_whole(destination, md5.hash[2]);
    format_hexadecimal_whole(destination, md5.hash[3]);
    return 32;
}

u32 format_arg_partial(char* destination, const MD5& md5, const minitl::format_options& options,
                       u32 reservedLength, u32 maxCapacity)
{
    motor_forceuse(options);
    motor_forceuse(reservedLength);
    using minitl::format_details::hexadecimal_format::format_hexadecimal_whole;
    u32 i = 0;
    while(maxCapacity >= 8)
    {
        destination += format_hexadecimal_whole(destination, md5.hash[i]);
        maxCapacity -= 8;
        ++i;
    }
    char buffer[8];
    format_hexadecimal_whole(buffer, md5.hash[i]);
    memcpy(destination, buffer, maxCapacity);
    return i * 8 + maxCapacity;
}

}  // namespace Motor
