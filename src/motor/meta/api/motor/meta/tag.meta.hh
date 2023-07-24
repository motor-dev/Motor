/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_TAG_META_HH
#define MOTOR_META_TAG_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

class motor_api(META) Tag
{
public:
    raw< const Tag > next;
    Value            tag;
};

}}  // namespace Motor::Meta

#endif
