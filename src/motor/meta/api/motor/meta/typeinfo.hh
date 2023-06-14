/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_TYPEINFO_HH
#define MOTOR_META_TYPEINFO_HH

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
    MOTOR_EXPORT static raw< const Class > klass();
    MOTOR_EXPORT static istring            name();
};

template < typename T >
struct TypeID
{
    static inline Type type()
    {
        return Type::makeType(ClassID< T >::klass(), Type::Indirection::Value,
                              Type::Constness::Mutable, Type::Constness::Mutable);
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
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::Value,
                              Type::Constness::Const, Type::Constness::Const);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("{0} {1}"), TypeID< T >::name(), "const"));
        return result;
    }
};

template < typename T >
struct TypeID< T& >
{
    static inline Type type()
    {
        Type t      = TypeID< T >::type();
        t.access    = Type::Constness::Mutable;
        t.constness = Type::Constness::Const;
        return t;
    }
    static inline istring name()
    {
        static istring result = istring(minitl::format< 1024u >(FMT("{0}&"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< const T& >
{
    static inline Type type()
    {
        Type t   = TypeID< T >::type();
        t.access = Type::Constness::Const;
        return t;
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("{0} const&"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< ref< T > >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::RefPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Mutable);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("ref<{0}>"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< weak< T > >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::WeakPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Mutable);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("weak<{0}>"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< raw< T > >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::RawPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Mutable);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("raw<{0}>"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< T* >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::RawPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Mutable);
    }
    static inline istring name()
    {
        static istring result = istring(minitl::format< 1024u >(FMT("{0}*"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< ref< T > const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::RefPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Const);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("ref<{0}> const"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< weak< T > const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::WeakPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Const);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("weak<{0}> const"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< raw< T > const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::RawPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Const);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("raw<{0}> const"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< T* const >
{
    static inline Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::RawPtr,
                              minitl::is_const< T >() ? Type::Constness::Const
                                                      : Type::Constness::Mutable,
                              Type::Constness::Const);
    }
    static inline istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("{0}* const"), TypeID< T >::name()));
        return result;
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

#endif
