/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/namespace.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/operatortable.hh>
#include <motor/meta/property.meta.hh>
#include <motor/meta/tag.meta.hh>
#include <motor/meta/value.hh>

namespace Motor {
namespace Meta {

void Class::copy(const void* src, void* dst) const
{
    if(motor_assert_format(copyconstructor, "no copy for type {0}", name)) return;
    (*copyconstructor)(src, dst);
}

void Class::destroy(void* src) const
{
    if(motor_assert_format(destructor, "no destructor for type {0}", name)) return;
    (*destructor)(src);
}

void Class::enumerateObjects(EnumerateRecursion recursion, EnumerateCallback callback) const
{
    static raw< const Class > const s_metaClass = motor_class< Class >();
    raw< const Object >             o           = objects;
    while(o)
    {
        (*callback)(o->value);
        if(recursion == EnumerateRecursive && (o->value.type().metaclass == s_metaClass))
        {
            o->value.as< raw< const Class > >()->enumerateObjects(recursion, callback);
        }
        o = o->next;
    }
}

raw< const Property > Class::getProperty(istring propertyName) const
{
    for(raw< const Property > p = properties; p; p = p->next)
    {
        if(p->name == propertyName)
        {
            raw< const Property > pptr = {p};
            return pptr;
        }
    }
    return {};
}

raw< const Method > Class::getMethod(istring methodName) const
{
    for(raw< const Method > m = methods; m; m = m->next)
    {
        if(m->name == methodName)
        {
            raw< const Method > mptr = {m};
            return mptr;
        }
    }
    return {};
}

raw< const Object > Class::getStaticProperty(istring propertyName) const
{
    raw< const Object > o = this->objects;
    while(o)
    {
        if(o->name == propertyName)
        {
            break;
        }
        o = o->next;
    }
    return o;
}

Value Class::get(Value& from, istring propname, bool& found) const
{
    static raw< const Class > const s_metaClass = motor_class< Class >();
    if(from.type().metaclass == s_metaClass)
    {
        auto                cls = from.as< raw< const Class > >();
        raw< const Object > o   = cls->getStaticProperty(propname);
        if(o)
        {
            found = true;
            return o->value;
        }
        raw< const Method > m = cls->getMethod(propname);
        if(m)
        {
            found = true;
            return Value(m);
        }
    }

    raw< const Property > p = getProperty(propname);
    if(p)
    {
        found = true;
        return p->get(from);
    }
    raw< const Method > m = getMethod(propname);
    if(m)
    {
        found = true;
        return Value(m);
    }

    found = false;
    return {};
}

Value Class::get(const Value& from, istring propname, bool& found) const
{
    static raw< const Class > const s_metaClass = motor_class< Class >();
    if(from.type().metaclass == s_metaClass)
    {
        auto                cls = from.as< raw< const Class > >();
        raw< const Object > o   = cls->getStaticProperty(propname);
        if(o)
        {
            found = true;
            return o->value;
        }
        raw< const Method > m = cls->getMethod(propname);
        if(m)
        {
            found = true;
            return Value(m);
        }
    }

    raw< const Property > p = getProperty(propname);
    if(p)
    {
        found = true;
        return p->get(from);
    }
    raw< const Method > m = getMethod(propname);
    if(m)
    {
        found = true;
        return Value(m);
    }

    found = false;
    return {};
}

bool Class::isA(raw< const Class > klass) const
{
    raw< const Class > ci = {this};
    while(ci)
    {
        if(ci == klass) return true;
        ci = ci->base;
    }
    return false;
}

Value Class::getTag(const Type& type) const
{
    for(raw< const Tag > tag = tags; tag; tag = tag->next)
    {
        if(type <= tag->tag.type()) return Value(Value::ByRef(tag->tag));
    }
    return {};
}

Value Class::getTag(raw< const Class > type) const
{
    return getTag(Type::makeType(type, Type::Indirection::Value, Type::Constness::Const,
                                 Type::Constness::Const));
}

bool Class::distance(raw< const Class > other, u16& result) const
{
    raw< const Class > ci = {this};
    result                = 0;
    while(ci)
    {
        if(ci == other) return true;
        ci = ci->base;
        ++result;
    }
    return false;
}

Value Class::findClass(inamespace name)
{
    Value v = Value(raw< const Meta::Class >(motor_motor_Namespace()));
    while(v && name.size())
    {
        v = v[name.pop_front()];
    }
    return v;
}

}  // namespace Meta

raw< Meta::Class > motor_motor_Namespace()
{
    static Meta::Class ci     = {istring("Motor"),
                                 0,
                                 motor_class< void >(),
                                 0,
                                 {nullptr},
                                 {nullptr},
                                 {nullptr},
                                 {nullptr},
                                 {nullptr},
                                 motor_class< void >()->operators,
                                 nullptr,
                                 nullptr};
    raw< Meta::Class > result = {&ci};
    return result;
}

}  // namespace Motor
