/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_PROPERTYINFO_SCRIPT_HH_
#define MOTOR_META_ENGINE_PROPERTYINFO_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/engine/helper/staticarray.hh>
#include <motor/meta/typeinfo.script.hh>

namespace Motor { namespace Meta {

struct Tag;
class Value;

struct motor_api(META) Property
{
    friend class Value;
published:
    raw< const staticarray< const Tag > > tags;
    istring                               name;
    Type                                  owner;
    Type                                  type;

    Value get(Value & from) const;
    Value get(const Value& from) const;
    void  set(Value & from, const Value& value) const;

    Value getTag(const Type& tagType) const;
    Value getTag(raw< const Class > tagType) const;

public:
    Value (*getter)(void* data, bool isConst);
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
