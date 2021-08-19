/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TYPEINFO_HH_
#define MOTOR_META_TYPEINFO_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/typeinfo.script.hh>
#include <motor/minitl/typemanipulation.hh>

namespace Motor { namespace Meta {

struct Class;
struct Property;
struct Method;

}}  // namespace Motor::Meta

template < typename T >
static inline Motor::Meta::Type motor_type();
template < typename T >
static inline raw< const Motor::Meta::Class > motor_class();

namespace Motor { namespace Meta {

template < typename T >
struct ClassID
{
    static MOTOR_EXPORT raw< const Meta::Class > klass();
};

template < typename T >
struct TypeID
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(ClassID< T >::klass(), Meta::Type::Value, Meta::Type::Mutable,
                                    Meta::Type::Mutable);
    }
};

template < typename T >
struct TypeID< const T > : public TypeID< T >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::Value,
                                    Meta::Type::Const, Meta::Type::Const);
    }
};

template < typename T >
struct TypeID< T& >
{
    static inline Meta::Type type()
    {
        Meta::Type t = TypeID< T >::type();
        t.access     = Meta::Type::Mutable;
        t.constness  = Meta::Type::Const;
        return t;
    }
};

template < typename T >
struct TypeID< const T& >
{
    static inline Meta::Type type()
    {
        Meta::Type t = TypeID< T >::type();
        t.access     = Meta::Type::Const;
        return t;
    }
};

template < typename T >
struct TypeID< ref< T > >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::RefPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Mutable);
    }
};

template < typename T >
struct TypeID< weak< T > >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::WeakPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Mutable);
    }
};

template < typename T >
struct TypeID< raw< T > >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::RawPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Mutable);
    }
};

template < typename T >
struct TypeID< T* >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::RawPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Mutable);
    }
};

template < typename T >
struct TypeID< ref< T > const >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::RefPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Const);
    }
};

template < typename T >
struct TypeID< weak< T > const >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::WeakPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Const);
    }
};

template < typename T >
struct TypeID< raw< T > const >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::RawPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Const);
    }
};

template < typename T >
struct TypeID< T* const >
{
    static inline Meta::Type type()
    {
        return Meta::Type::makeType(TypeID< T >::type().metaclass, Meta::Type::RawPtr,
                                    minitl::is_const< T >::Value ? Meta::Type::Const
                                                                 : Meta::Type::Mutable,
                                    Meta::Type::Const);
    }
};

template < typename T >
struct TypeID< scoped< T > >
{
};

}}  // namespace Motor::Meta

template < typename T >
static inline Motor::Meta::Type motor_type()
{
    return Motor::Meta::TypeID< T >::type();
}

template < typename T >
static inline raw< const Motor::Meta::Class > motor_class()
{
    return Motor::Meta::ClassID< T >::klass();
}

/**************************************************************************************************/
#endif
