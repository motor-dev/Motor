/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TAGS_DOCUMENTATION_META_HH_
#define MOTOR_META_TAGS_DOCUMENTATION_META_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>

namespace Motor { namespace Meta {

struct motor_api(META) Documentation
{
public:
    u64       size;
    const u8* bytes;
published:
    Documentation(u64 size, const u8* gzipBytes) : size(size), bytes(gzipBytes)
    {
    }
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
