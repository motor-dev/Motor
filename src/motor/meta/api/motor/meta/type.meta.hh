/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_TYPE_META_HH
#define MOTOR_META_TYPE_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/conversioncost.hh>

namespace Motor { namespace Meta {

class Value;
class Class;

struct motor_api(META) Type
{
    friend class Value;

    enum struct Indirection : u8
    {
        Value   = 0,
        RawPtr  = 1,
        WeakPtr = 2,
        RefPtr  = 3
    };

    enum struct Constness : u8
    {
        Const   = 0,
        Mutable = 1
    };
    enum MakeConstType
    {
        MakeConst
    };

    raw< const Class > metaclass;
    Indirection        indirection;
    Constness          access;
    Constness          constness;

    static inline Type makeType(raw< const Class > klass, Indirection indirection, Constness access,
                                Constness constness)
    {
        Type info = {klass, indirection, access, constness};
        return info;
    }
    static inline Type makeType(const Type& type, MakeConstType constify)
    {
        motor_forceuse(constify);
        Type info = {type.metaclass, type.indirection, type.access, Constness::Const};
        return info;
    }
    u32  size() const;
    bool isA(const Type& other) const;
    bool isConst() const
    {
        return indirection == Indirection::Value ? (constness == Constness::Const)
                                                 : (access == Constness::Const);
    }

public:
    template < typename T >
    [[motor::meta(export = no)]] bool           isA() const;
    [[motor::meta(export = no)]] ConversionCost calculateConversionTo(const Type& other) const;

private:
    void* rawget(const void*) const;
    void  copy(const void* source, void* dest) const;
    void  destroy(void* obj) const;
};

}}  // namespace Motor::Meta

namespace motor_meta(export = no) Motor { namespace Meta {

motor_api(META) bool         operator==(Type t1, Type t2);
motor_api(META) bool         operator<=(Type t1, Type t2);
static inline ConversionCost calculateConversionTo(const Type& from, const Type& target)
{
    return from.calculateConversionTo(target);
}

motor_api(META) u32 format_length(const Type& type, const minitl::format_options& options);
motor_api(META) u32 format_arg(char* destination, const Type& type,
                               const minitl::format_options& options, u32 reservedLength);
motor_api(META) u32
    format_arg_partial(char* destination, const Type& type, const minitl::format_options& options,
                       u32 reservedLength, u32 maxCapacity);

}}  // namespace motor_meta(export=no)Motor::Meta

#endif
