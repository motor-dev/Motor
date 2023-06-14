/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_CLASSINFO_META_HH
#define MOTOR_META_CLASSINFO_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/builtin.hh>
#include <motor/meta/engine/helper/staticarray.hh>

namespace Motor {
namespace Meta {

class Value;
struct ObjectInfo;
struct Property;
struct Method;
struct Tag;
struct OperatorTable;
template < typename T >
struct staticarray;
struct Type;

enum ClassType
{
    ClassType_Object,
    ClassType_Struct,
    ClassType_Pod,
    ClassType_Namespace,
    ClassType_Array,
    ClassType_Enum,
    ClassType_String,
    ClassType_Number,
    ClassType_Vector2,
    ClassType_Vector3,
    ClassType_Vector4,
    ClassType_Vector8,
    ClassType_Vector16,
    ClassType_Variant
};

motor_tag(Index(ClassType_Namespace)) struct motor_api(META) Class
{
    friend struct Type;
    friend class Value;
published:
    static istring nameOperatorCall();
    static istring nameConstructor();
published:
    istring const                                 name;
    u32 const                                     size;
    i32 const                                     offset;
    u32 const                                     id;
    raw< const Class > const                      owner;
    raw< const Class > const                      parent;
    mutable raw< const ObjectInfo >               objects;
    raw< const staticarray< const Tag > >         tags;
    staticarray< const Property >                 properties;
    staticarray< const Method >                   methods;
    motor_tag(Alias("?call")) raw< const Method > constructor;

public:
    raw< const OperatorTable > operators;
    typedef void (*CopyConstructor)(const void* source, void* destination);
    typedef void (*Destructor)(void* object);
    const CopyConstructor copyconstructor;
    const Destructor      destructor;
published:
    typedef enum ClassType ClassType;
    Value                  getTag(const Type& type) const;
    Value                  getTag(raw< const Class > type) const;

    Value get(Value & from, istring name, bool& found) const;
    Value get(const Value& from, istring name, bool& found) const;

    bool isA(raw< const Class > klass) const;

    inamespace fullname() const;

    inline ClassType type() const
    {
        return ClassType(id & 0xffff);
    }
    inline u32 index() const
    {
        return id >> 16;
    }

    raw< const Property >   getProperty(istring propertyName) const;
    raw< const Method >     getMethod(istring methodName) const;
    raw< const ObjectInfo > getStaticProperty(istring propertyName) const;
    static Value            findClass(inamespace name);

public:
    typedef void (*EnumerateCallback)(const Value& v);
    enum EnumerateRecursion
    {
        EnumerateOwn,
        EnumerateRecursive
    };
    void enumerateObjects(EnumerateRecursion recursion, EnumerateCallback callback) const;
    bool distance(raw< const Class > other, u16 & result) const;

private:  // friend Value
    void copy(const void* src, void* dst) const;
    void destroy(void* src) const;
};

}  // namespace Meta

MOTOR_EXPORT raw< Meta::Class > motor_motor_Namespace();
MOTOR_EXPORT raw< Meta::Class > motor_motor_Namespace_Motor();

}  // namespace Motor

#endif
