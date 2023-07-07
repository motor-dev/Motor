/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/call.hh>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/tag.meta.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

const Value Method::Parameter::s_noDefaultValue;

Value Method::Parameter::getTag(const Type& tagType) const
{
    for(raw< const Tag > tag = tags; tag; tag = tag->next)
    {
        if(tagType <= tag->tag.type()) return Value(Value::ByRef(tag->tag));
    }
    return {};
}

Value Method::Parameter::getTag(raw< const Class > tagType) const
{
    return this->getTag(Type::makeType(tagType, Type::Indirection::Value, Type::Constness::Const,
                                       Type::Constness::Const));
}

Value Method::Overload::getTag(const Type& type) const
{
    for(raw< const Tag > tag = tags; tag; tag = tag->next)
    {
        if(type <= tag->tag.type()) return Value(Value::ByRef(tag->tag));
    }
    return {};
}

Value Method::Overload::getTag(raw< const Class > type) const
{
    return getTag(Type::makeType(type, Type::Indirection::Value, Type::Constness::Const,
                                 Type::Constness::Const));
}

Value Method::doCall(Value* params, u32 paramCount) const
{
    auto* args = static_cast< ArgInfo< Type >* >(malloca(sizeof(ArgInfo< Type >) * paramCount));
    for(u32 i = 0; i < paramCount; ++i)
    {
        new(&args[i]) ArgInfo< Type >(params[i].type());
    }
    CallInfo c = resolve< Type >({this}, {args, args + paramCount}, {nullptr, nullptr});
    if(c.conversion < ConversionCost::s_incompatible)
    {
        return c.overload->call({this}, params, paramCount);
    }
    else
    {
        motor_error(Log::meta(), "No overload can convert all parameters");
        return {};
    }
}

}}  // namespace Motor::Meta
