/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_TAGS_DOCUMENTATION_META_HH
#define MOTOR_META_TAGS_DOCUMENTATION_META_HH

#include <motor/meta/stdafx.h>

namespace Motor { namespace Meta {

struct motor_api(META) Documentation
{
private:
    u64       size;
    const u8* bytes;

public:
    Documentation(u64 size, const u8* gzipBytes) : size(size), bytes(gzipBytes)
    {
        motor_forceuse(this->size);
        motor_forceuse(this->bytes);
    }
};

}}  // namespace Motor::Meta

#include <motor/meta/tags/documentation.meta.factory.hh>
#endif
