/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_CLASS_META_HH
#define MOTOR_META_CLASS_META_HH

#include <motor/meta/stdafx.h>

namespace Motor {
namespace Meta {

class Value;
class Object;
class Property;
class Method;
class Tag;
class InterfaceTable;
struct Type;

class motor_api(META) Class
{
    friend struct Type;
    friend class Value;

public:
    [[motor::meta(noexport)]] typedef void (*CopyConstructor)(const void* source,
                                                              void*       destination);
    [[motor::meta(noexport)]] typedef void (*Destructor)(void* object);

public:
    istring const               name;
    u32 const                   size;
    raw< const Class > const    base;
    i32 const                   baseOffset;
    raw< const Object >         objects;
    raw< const Tag > const      tags;
    raw< const Property > const properties;
    raw< const Method > const   methods;
    raw< const Method >         constructor;

public:
    [[motor::meta(noexport)]] raw< const InterfaceTable > const interfaces;
    [[motor::meta(noexport)]] const CopyConstructor             copyconstructor;
    [[motor::meta(noexport)]] const Destructor                  destructor;

public:
    Value getTag(const Type& type) const;
    Value getTag(raw< const Class > type) const;

    Value get(Value & from, istring name, bool& found) const;
    Value get(const Value& from, istring name, bool& found) const;

    bool isA(raw< const Class > klass) const;

    raw< const Property > getProperty(istring propertyName) const;
    raw< const Method >   getMethod(istring methodName) const;
    raw< const Object >   getStaticProperty(istring propertyName) const;
    static Value          findClass(inamespace name);

public:
    [[motor::meta(noexport)]] typedef void (*EnumerateCallback)(const Value& v);
    enum [[motor::meta(noexport)]] EnumerateRecursion {EnumerateOwn, EnumerateRecursive};
    [[motor::meta(noexport)]] void enumerateObjects(EnumerateRecursion recursion,
                                                    EnumerateCallback  callback) const;
    [[motor::meta(noexport)]] bool distance(raw< const Class > other, u16 & result) const;

private:  // friend Value
    void copy(const void* src, void* dst) const;
    void destroy(void* src) const;
};

}  // namespace Meta

MOTOR_EXPORT raw< Meta::Class > motor_motor_Namespace();
MOTOR_EXPORT raw< Meta::Class > motor_motor_Namespace_Motor();

}  // namespace Motor

#endif
