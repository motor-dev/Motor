/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TYPEINFO_META_HH_
#define MOTOR_META_TYPEINFO_META_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/conversion.meta.hh>

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
    bool                           isA() const;
    minitl::format_buffer< 1024u > name() const;
    bool                           isConst() const
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

#include <motor/meta/typeinfo_format.hh>

/**************************************************************************************************/
#endif
