/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/call.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/taginfo.meta.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

const Value Method::Parameter::s_noDefaultValue;

Value Method::Parameter::getTag(const Type& tagType) const
{
    if(tags)
    {
        for(const auto& tag: *tags)
        {
            if(tagType <= tag.tag.type()) return Value(Value::ByRef(tag.tag));
        }
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
    if(tags)
    {
        for(const auto& tag: *tags)
        {
            if(type <= tag.tag.type()) return Value(Value::ByRef(tag.tag));
        }
    }
    return {};
}

Value Method::Overload::getTag(raw< const Class > type) const
{
    return getTag(Type::makeType(type, Type::Indirection::Value, Type::Constness::Const,
                                 Type::Constness::Const));
}

minitl::format_buffer< 1024u > Method::Overload::signature() const
{
    minitl::format_buffer< 1024u > result {};
    char*                          current = result.buffer;
    char*                          end     = result.buffer + 1023;
    *end                                   = 0;
    for(u32 i = 0; i < params.count; ++i)
    {
        minitl::format_buffer< 1024u > argType
            = minitl::format< 1024 >(FMT("{0}"), params.elements[i].type);
        for(const char* arg = argType; *arg && current != end; ++arg, ++current)
            *current = *arg;
        if(current != end) *(current++) = ' ';
        for(const char* arg = params.elements[i].name.c_str(); *arg && current != end;
            ++arg, ++current)
            *current = *arg;
        if(i < params.count - 1)
        {
            if(current != end) *(current++) = ',';
            if(current != end) *(current++) = ' ';
        }
    }
    *current = 0;
    if(current == end)
    {
        *(current - 3) = '.';
        *(current - 2) = '.';
        *(current - 1) = '.';
    }
    return result;
}

Value Method::doCall(Value* params, u32 paramCount) const
{
    auto* args = static_cast< ArgInfo< Type >* >(malloca(sizeof(ArgInfo< Type >) * paramCount));
    for(u32 i = 0; i < paramCount; ++i)
    {
        new(&args[i]) ArgInfo< Type >(params[i].type());
    }
    CallInfo c = resolve({this}, args, paramCount);
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
