/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TYPEINFO_SCRIPT_HH_
#define MOTOR_META_TYPEINFO_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.script.hh>
#include <motor/meta/conversion.script.hh>

namespace Motor { namespace Meta {

class Value;
struct Class;

struct motor_api(META) Type
{
    friend class Value;

    enum Indirection
    {
        Value   = 0,
        RawPtr  = 1,
        WeakPtr = 2,
        RefPtr  = 3
    };

    enum Constness
    {
        Const   = 0,
        Mutable = 1
    };
    enum MakeConstType
    {
        MakeConst
    };

    raw< const Class > metaclass;
    u16                indirection;
    u8                 access;
    u8                 constness;

    static inline Type makeType(raw< const Class > klass, Indirection indirection, Constness access,
                                Constness constness)
    {
        Type info = {klass, (u16)indirection, (u8)access, (u8)constness};
        return info;
    }
    static inline Type makeType(const Type& type, MakeConstType constify)
    {
        motor_forceuse(constify);
        Type info = {type.metaclass, type.indirection, type.access, Const};
        return info;
    }
    u32            size() const;
    bool           isA(const Type& other) const;
    ConversionCost calculateConversion(const Type& other) const;

public:
    template < typename T >
    bool                    isA() const;
    minitl::format< 1024u > name() const;
    bool                    isConst() const
    {
        return indirection == Value ? (constness == 0) : (access == 0);
    }

private:
    void* rawget(const void*) const;
    void  copy(const void* source, void* dest) const;
    void  create(void* obj) const;
    void  destroy(void* obj) const;
};

motor_api(META) bool         operator==(Type t1, Type t2);
motor_api(META) bool         operator<=(Type t1, Type t2);
static inline ConversionCost calculateConversion(const Type& type, const Type& target)
{
    return type.calculateConversion(target);
}

}}  // namespace Motor::Meta

namespace minitl {

template < u16 SIZE >
const minitl::format< SIZE >& operator|(const minitl::format< SIZE >& format,
                                        const Motor::Meta::Type&      type)
{
    minitl::format< 4096 > typeName("%s%s%s%s%s");
    if(type.constness == Motor::Meta::Type::Const)
    {
        typeName | "const ";
    }
    else
    {
        typeName | "";
    }
    const char* constness = "";
    if(type.access == Motor::Meta::Type::Const)
    {
        constness = "const ";
    }
    switch(type.indirection)
    {
    case Motor::Meta::Type::RefPtr:
        typeName | "ref<" | constness | type.metaclass->fullname() | ">";
        break;
    case Motor::Meta::Type::WeakPtr:
        typeName | "weak<" | constness | type.metaclass->fullname() | ">";
        break;
    case Motor::Meta::Type::RawPtr:
        typeName | "raw<" | constness | type.metaclass->fullname() | ">";
        break;
    case Motor::Meta::Type::Value: typeName | "" | "" | type.metaclass->fullname() | ""; break;
    default: motor_notreached(); break;
    }
    return format | typeName.c_str();
}

}  // namespace minitl

/**************************************************************************************************/
#endif
