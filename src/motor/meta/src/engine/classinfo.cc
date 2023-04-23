/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>
#include <motor/meta/engine/taginfo.meta.hh>
#include <motor/meta/value.hh>

namespace Motor {
namespace Meta {

motor_api(META) char s_zero[] = {0, 0, 0, 0};

istring Class::nameConstructor()
{
    static const istring result = "?new";
    return result;
}

istring Class::nameDestructor()
{
    static const istring result = "?del";
    return result;
}

istring Class::nameOperatorCall()
{
    static const istring result = "?call";
    return result;
}

istring Class::nameOperatorIndex()
{
    static const istring result = "?[]";
    return result;
}

istring Class::nameOperatorLessThan()
{
    static const istring result = "?<";
    return result;
}

istring Class::nameOperatorGreaterThan()
{
    static const istring result = "?>";
    return result;
}

istring Class::nameOperatorLessThanOrEqual()
{
    static const istring result = "?<=";
    return result;
}

istring Class::nameOperatorGreaterThanOrEqual()
{
    static const istring result = "?>=";
    return result;
}

istring Class::nameOperatorMultiply()
{
    static const istring result = "?*";
    return result;
}

istring Class::nameOperatorDivide()
{
    static const istring result = "?*";
    return result;
}

istring Class::nameOperatorModulo()
{
    static const istring result = "?%";
    return result;
}

istring Class::nameOperatorAdd()
{
    static const istring result = "?+";
    return result;
}

istring Class::nameOperatorSubstract()
{
    static const istring result = "?-";
    return result;
}

istring Class::nameOperatorShiftLeft()
{
    static const istring result = "?<<";
    return result;
}

istring Class::nameOperatorShiftRight()
{
    static const istring result = "?>>";
    return result;
}

istring Class::nameOperatorBitwiseAnd()
{
    static const istring result = "?&";
    return result;
}

istring Class::nameOperatorBitwiseOr()
{
    static const istring result = "?|";
    return result;
}

istring Class::nameOperatorBitwiseXor()
{
    static const istring result = "?^";
    return result;
}

istring Class::nameOperatorBitwiseNot()
{
    static const istring result = "?~";
    return result;
}

istring Class::nameOperatorLogicalAnd()
{
    static const istring result = "?&&";
    return result;
}

istring Class::nameOperatorLogicalOr()
{
    static const istring result = "?||";
    return result;
}

istring Class::nameOperatorLogicalNot()
{
    static const istring result = "?!";
    return result;
}

istring Class::nameOperatorEqual()
{
    static const istring result = "?==";
    return result;
}

istring Class::nameOperatorNotEqual()
{
    static const istring result = "?!=";
    return result;
}

istring Class::nameOperatorAssign()
{
    static const istring result = "?=";
    return result;
}

istring Class::nameOperatorMultiplyAssign()
{
    static const istring result = "?*=";
    return result;
}

istring Class::nameOperatorDivideAssign()
{
    static const istring result = "?/=";
    return result;
}

istring Class::nameOperatorModuloAssign()
{
    static const istring result = "?%=";
    return result;
}

istring Class::nameOperatorAddAssign()
{
    static const istring result = "?+=";
    return result;
}

istring Class::nameOperatorSubstractAssign()
{
    static const istring result = "?-=";
    return result;
}

istring Class::nameOperatorShiftLeftAssign()
{
    static const istring result = "?<<=";
    return result;
}

istring Class::nameOperatorShiftRightAssign()
{
    static const istring result = "?>>=";
    return result;
}

istring Class::nameOperatorAndAssign()
{
    static const istring result = "?&=";
    return result;
}

istring Class::nameOperatorOrAssign()
{
    static const istring result = "?|=";
    return result;
}

istring Class::nameOperatorXorAssign()
{
    static const istring result = "?^=";
    return result;
}

istring Class::nameOperatorIncrement()
{
    static const istring result = "?++";
    return result;
}

istring Class::nameOperatorDecrement()
{
    static const istring result = "?--";
    return result;
}

istring Class::nameOperatorGet()
{
    static const istring result = "?->";
    return result;
}

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
    raw< const ObjectInfo >         o           = objects;
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
    raw< const Class > thisCls {this};
    for(raw< const Class > cls = thisCls; cls; cls = cls->parent)
    {
        for(const Property* p = cls->properties.begin(); p != cls->properties.end(); ++p)
        {
            if(p->name == propertyName)
            {
                raw< const Property > pptr = {p};
                return pptr;
            }
        }
    }
    return {};
}

raw< const Method > Class::getMethod(istring methodName) const
{
    raw< const Class > thisCls = {this};
    for(raw< const Class > cls = thisCls; cls; cls = cls->parent)
    {
        for(const Method* m = cls->methods.begin(); m != cls->methods.end(); ++m)
        {
            if(m->name == methodName)
            {
                raw< const Method > mptr = {m};
                return mptr;
            }
        }
    }
    return {};
}

raw< const ObjectInfo > Class::getStaticProperty(istring propertyName) const
{
    raw< const ObjectInfo > o = this->objects;
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
        raw< const Class >      cls = from.as< raw< const Class > >();
        raw< const ObjectInfo > o   = cls->getStaticProperty(propname);
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
        raw< const Class >      cls = from.as< raw< const Class > >();
        raw< const ObjectInfo > o   = cls->getStaticProperty(propname);
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
        ci = ci->parent;
    }
    return false;
}

Value Class::getTag(const Type& type) const
{
    raw< const Class > thisCls = {this};
    for(raw< const Class > cls = thisCls; cls; cls = cls->parent)
    {
        if(cls->tags)
        {
            for(const auto& tag: *cls->tags)
            {
                if(type <= tag.tag.type()) return Value(Value::ByRef(tag.tag));
            }
        }
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
        ci = ci->parent;
        ++result;
    }
    return false;
}

inamespace Class::fullname() const
{
    if(!owner)
    {
        return inamespace(name);
    }
    else
    {
        return owner->fullname() + name;
    }
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
    static Meta::Class ci     = {"Motor",
                                 0,
                                 0,
                                 Meta::ClassType_Namespace,
                                 {nullptr},
                                 {nullptr},
                                 {nullptr},
                                 {nullptr},
                                 {0, nullptr},
                                 {0, nullptr},
                                 {nullptr},
                                 Meta::OperatorTable::s_emptyTable,
                                 nullptr,
                                 nullptr};
    raw< Meta::Class > result = {&ci};
    return result;
}

}  // namespace Motor
