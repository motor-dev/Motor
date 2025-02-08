/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/property.meta.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

u32 Type::size() const
{
    switch(indirection)
    {
    case Indirection::Value: return metaclass->size;
    case Indirection::RawPtr: return sizeof(raw< char >);
    case Indirection::RefPtr: return sizeof(ref< minitl::pointer >);
    case Indirection::WeakPtr: return sizeof(weak< minitl::pointer >);
    default: motor_notreached(); return 0;
    }
}

const void* Type::rawget(const void* data) const
{
    switch(indirection)
    {
    case Indirection::Value: return data;
    case Indirection::RawPtr: return *static_cast< void** >(const_cast< void* >(data));
    case Indirection::RefPtr:
        return static_cast< const ref< minitl::pointer >* >(data)->operator->();
    case Indirection::WeakPtr:
        return static_cast< const weak< minitl::pointer >* >(data)->operator->();
    default: motor_notreached(); return nullptr;
    }
}

void* Type::rawget(void* data) const
{
    switch(indirection)
    {
    case Indirection::Value: return data;
    case Indirection::RawPtr: return *static_cast< void** >(data);
    case Indirection::RefPtr: return static_cast< ref< minitl::pointer >* >(data)->operator->();
    case Indirection::WeakPtr: return static_cast< weak< minitl::pointer >* >(data)->operator->();
    default: motor_notreached(); return nullptr;
    }
}

void Type::copy(const void* source, void* dest) const
{
    switch(indirection)
    {
    case Indirection::Value: return metaclass->copy(source, dest);
    case Indirection::RawPtr: memcpy(dest, source, sizeof(void*)); return;
    case Indirection::RefPtr:
        new(dest) const ref< const minitl::pointer >(
            *static_cast< const ref< const minitl::pointer >* >(source));
        return;
    case Indirection::WeakPtr:
        new(dest) const weak< const minitl::pointer >(
            *static_cast< const weak< const minitl::pointer >* >(source));
        return;
    default: motor_notreached(); return;
    }
}

void Type::destroy(void* ptr) const
{
    switch(indirection)
    {
    case Indirection::Value: return metaclass->destroy(ptr);
    case Indirection::RawPtr: return;
    case Indirection::RefPtr: static_cast< ref< const minitl::pointer >* >(ptr)->~ref(); return;
    case Indirection::WeakPtr: static_cast< weak< const minitl::pointer >* >(ptr)->~weak(); return;
    default: motor_notreached(); return;
    }
}

ConversionCost Type::calculateConversionTo(const Type& other) const
{
    ConversionCost result;

    if(other.metaclass->interfaces->variantInterface) return ConversionCost::s_variant;
    if(other.indirection > Indirection::Value && access < other.access)
        return ConversionCost::s_incompatible;
    else if(other.indirection > Indirection::Value)
        result.qualification += u16(access) - u16(other.access);

    if(indirection < other.indirection)
        return ConversionCost::s_incompatible;
    else
        result.qualification += u16(indirection) - u16(other.indirection);

    if(metaclass->distance(other.metaclass, result.promotion))
        return result;
    else
        return ConversionCost::s_incompatible;
}

bool Type::isA(const Type& other) const
{
    return other.indirection <= indirection
           && u32(indirection) * u32(other.access) <= u32(indirection) * u32(access)
           && metaclass->isA(other.metaclass);
}

bool operator==(Type t1, Type t2)
{
    return t1.metaclass == t2.metaclass && t1.indirection == t2.indirection
           && t1.access == t2.access && t1.constness == t2.constness;
}

bool operator<=(Type t1, Type t2)
{
    return (t1.indirection <= t2.indirection) && t1.access <= t2.access
           && t2.metaclass->isA(t1.metaclass);
}

u32 format_length(const Type& type, const minitl::format_options& options)
{
    u32 result = format_length(type.metaclass->fullname(), options);
    if(type.access == Type::Constness::Const) result += 6;
    if(type.constness == Type::Constness::Const && type.indirection != Type::Indirection::Value)
        result += 6;
    if(type.indirection == Type::Indirection::RawPtr
       || type.indirection == Type::Indirection::RefPtr)
        result += 5;
    else if(type.indirection == Type::Indirection::WeakPtr)
        result += 6;
    return result;
}

u32 format_arg(char* destination, const Type& type, const minitl::format_options& options,
               u32 reservedLength)
{
    u32 offset = 0;
    if(type.access == Type::Constness::Const)
    {
        memcpy(destination + offset, "const ", 6);  // NOLINT(bugprone-not-null-terminated-result)
        offset += 6;
        reservedLength -= 6;
    }
    if(type.indirection == Type::Indirection::RawPtr)
    {
        memcpy(destination + offset, "raw<", 4);  // NOLINT(bugprone-not-null-terminated-result)
        offset += 4;
        reservedLength -= 5;
    }
    else if(type.indirection == Type::Indirection::WeakPtr)
    {
        memcpy(destination + offset, "weak<", 5);  // NOLINT(bugprone-not-null-terminated-result)
        offset += 5;
        reservedLength -= 6;
    }
    else if(type.indirection == Type::Indirection::RefPtr)
    {
        memcpy(destination + offset, "ref<", 4);  // NOLINT(bugprone-not-null-terminated-result)
        offset += 4;
        reservedLength -= 5;
    }
    if(type.constness == Type::Constness::Const && type.indirection != Type::Indirection::Value)
    {
        memcpy(destination + offset, "const ", 6);  // NOLINT(bugprone-not-null-terminated-result)
        offset += 6;
        reservedLength -= 6;
    }
    offset += format_arg(destination + offset, type.metaclass->fullname(), options, reservedLength);
    if(type.indirection != Type::Indirection::Value) destination[offset++] = '>';

    return offset;
}

u32 format_arg_partial(char* destination, const Type& type, const minitl::format_options& options,
                       u32 reservedLength, u32 maxCapacity)
{
    return minitl::format_details::format_arg_partial_delegate< const Type&,
                                                                minitl::formatter< 's' > >(
        destination, type, options, reservedLength, maxCapacity);
}

}}  // namespace Motor::Meta
