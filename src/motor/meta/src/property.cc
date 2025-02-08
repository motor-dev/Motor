/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/method.meta.hh>
#include <motor/meta/property.meta.hh>
#include <motor/meta/tag.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

Value Property::get(const Value& from) const
{
    motor_assert_format(from.type().metaclass->isA(owner.metaclass),
                        "getting property on object of type {0}, while expecting type {1}",
                        from.type(), owner);
    i32                   offset = from.type().metaclass->baseOffset - owner.metaclass->baseOffset;
    raw< const Property > this_  = {this};
    return (*getter)(
        this_, static_cast< const void* >(static_cast< const char* >(from.rawget()) + offset));
}

void Property::set(Value& from, const Value& value) const
{
    motor_assert_format(from.type().metaclass->isA(owner.metaclass),
                        "getting property on object of type {0}, while expecting type {1}",
                        from.type(), owner);
    i32                   offset = from.type().metaclass->baseOffset - owner.metaclass->baseOffset;
    raw< const Property > this_  = {this};
    (*setter)(this_, static_cast< void* >(static_cast< char* >(from.rawget()) + offset), value);
}

Value Property::getTag(const Type& tagType) const
{
    for(raw< const Tag > tag = tags; tag; tag = tag->next)
    {
        if(tagType <= tag->tag.type()) return Value(Value::ByRef(tag->tag));
    }
    return {};
}

Value Property::getTag(raw< const Class > tagType) const
{
    return this->getTag(Type::makeType(tagType, Type::Indirection::Value, Type::Constness::Const,
                                       Type::Constness::Const));
}

}}  // namespace Motor::Meta
