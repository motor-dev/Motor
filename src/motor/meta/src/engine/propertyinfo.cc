/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>
#include <motor/meta/engine/taginfo.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

Value Property::get(const Value& from) const
{
    motor_assert(from.type().metaclass->isA(owner.metaclass),
                 "getting property on object of type %s, while expecting type %s" | from.type()
                     | owner);
    i32                   offset = from.type().metaclass->offset - owner.metaclass->offset;
    raw< const Property > this_  = {this};
    return (*getter)(this_, (void*)((char*)from.rawget() + offset));
}

void Property::set(Value& from, const Value& value) const
{
    get(from) = value;
}

Value Property::getTag(const Type& tagType) const
{
    if(tags)
    {
        for(const Tag* tag = tags->begin(); tag != tags->end(); ++tag)
        {
            if(tagType <= tag->tag.type()) return Value(Value::ByRef(tag->tag));
        }
    }
    return Value();
}

Value Property::getTag(raw< const Class > tagType) const
{
    return getTag(Type::makeType(tagType, Type::Value, Type::Const, Type::Const));
}

}}  // namespace Motor::Meta
