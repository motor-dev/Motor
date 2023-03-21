/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TYPEINFO_HH_
#define MOTOR_META_TYPEINFO_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/typeinfo.meta.hh>
#include <motor/minitl/type_traits.hh>

namespace Motor { namespace Meta {

struct Class;
struct Property;
struct Method;

template < typename T >
struct ClassID
{
    static MOTOR_EXPORT raw< const Class > klass();
    static MOTOR_EXPORT istring            name();
};

template < typename T >
struct TypeID
{
    static inline Type type()
    {
        return Type::makeType(ClassID< T >::klass(), Type::Value, Type::Mutable, Type::Mutable);
    }
    static inline istring name()
    {
        return ClassID< T >::name();
    }
};

template < typename T >
struct TypeID< const T > : public TypeID< T >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Value, Type::Const, Type::Const);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("{0} {1}"), TypeID< T >::name(), "const"));
    }
};

template < typename T >
struct TypeID< T& >
{
    static inline Type type()
    {
        Type t      = TypeID< T >::type();
        t.access    = Type::Mutable;
        t.constness = Type::Const;
        return t;
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("{0}&"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< const T& >
{
    static inline Type type()
    {
        Type t   = TypeID< T >::type();
        t.access = Type::Const;
        return t;
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("{0} const&"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< ref< T > >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::RefPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Mutable);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("ref<{0}>"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< weak< T > >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::WeakPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Mutable);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("weak<{0}>"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< raw< T > >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::RawPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Mutable);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("raw<{0}>"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< T* >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::RawPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Mutable);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("{0}*"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< ref< T > const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::RefPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Const);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("ref<{0}> const"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< weak< T > const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::WeakPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Const);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("weak<{0}> const"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< raw< T > const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::RawPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Const);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("raw<{0}> const"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< T* const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::RawPtr,
                              minitl::is_const< T >() ? Type::Const : Type::Mutable, Type::Const);
    }
    static inline istring name()
    {
        return istring(minitl::format< 1024u >(FMT("{0}* const"), TypeID< T >::name()));
    }
};

template < typename T >
struct TypeID< scoped< T > >
{
};

}}  // namespace Motor::Meta

template < typename T >
Motor::Meta::Type motor_type()
{
    return Motor::Meta::TypeID< T >::type();
}

template < typename T >
raw< const Motor::Meta::Class > motor_class()
{
    return Motor::Meta::ClassID< T >::klass();
}

/**************************************************************************************************/
#endif
