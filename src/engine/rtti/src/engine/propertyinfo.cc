/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <rtti/stdafx.h>
#include    <rtti/engine/propertyinfo.script.hh>
#include    <rtti/engine/methodinfo.script.hh>
#include    <rtti/typeinfo.hh>
#include    <rtti/value.inl>

namespace BugEngine { namespace RTTI
{

Value PropertyInfo::get(Value& from) const
{
    be_assert(from.type() <= owner, "getting property on object of type %s, while expecting type %s" | from.type().name() | owner.name());
    i32 propoffset = offset + (from.type().metaclass->offset - owner.metaclass->offset);
    if (from.isConst())
    {
        return Value(TypeInfo::makeType(type, TypeInfo::Constify), (void*)((char*)from.rawget() + propoffset));
    }
    else
    {
        return Value(type, (void*)((char*)from.rawget() + propoffset));
    }
}

void PropertyInfo::set(Value& from, const Value& value) const
{
    get(from) = value;
}

}}
