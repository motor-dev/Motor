/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/md5.hh>

extern "C"
{
#include <md5/md5.h>
}

namespace Motor {

MD5 digest(const void* buffer, u64 size)
{
    MD5_CTX context;
    MD5Init(&context);
    MD5Update(&context, (unsigned char*)buffer, motor_checked_numcast< unsigned int >(size));
    MD5Final(&context);
    MD5 result = {{0, 0, 0, 0}};

    for(int i = 0; i < 4; ++i)
        result.hash[i] = context.digest[i * 4 + 0] << 0 | context.digest[i * 4 + 1] << 8
                         | context.digest[i * 4 + 2] << 16 | context.digest[i * 4 + 3] << 24;
    return result;
}

u32 format_length(const MD5& type, const minitl::format_options& options)
{
    motor_forceuse(type);
    motor_forceuse(options);
    return 0;
}

u32 format_arg(char* destination, const MD5& type, const minitl::format_options& options,
               u32 reservedLength)
{
    motor_forceuse(destination);
    motor_forceuse(type);
    motor_forceuse(options);
    motor_forceuse(reservedLength);
    return 0;
}

u32 format_arg_partial(char* destination, const MD5& type, const minitl::format_options& options,
                       u32 reservedLength, u32 maxCapacity)
{
    motor_forceuse(destination);
    motor_forceuse(type);
    motor_forceuse(options);
    motor_forceuse(reservedLength);
    motor_forceuse(maxCapacity);
    return 0;
}
}  // namespace Motor
