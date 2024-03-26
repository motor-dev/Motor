/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_TYPEINFO_HH
#define MOTOR_META_TYPEINFO_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.hh>
#include <motor/meta/type.meta.hh>
#include <motor/minitl/type_traits.hh>

namespace Motor { namespace Meta {

template < typename T >
struct TypeID
{
    static constexpr Type type()
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
struct TypeID< const T >
{
    static constexpr Type type()
    {
        return Type::makeType(TypeID< T >::type().metaclass, Type::Indirection::Value,
                              Type::Constness::Const, Type::Constness::Const);
    }
    static istring name()
    {
        static istring result
            = istring(minitl::format< 1024u >(FMT("{0} const"), TypeID< T >::name()));
        return result;
    }
};

template < typename T >
struct TypeID< T& >
{
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
    static constexpr Type type()
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
constexpr Motor::Meta::Type motor_type()
{
    return Motor::Meta::TypeID< T >::type();
}

template < typename T >
constexpr raw< const Motor::Meta::Class > motor_class()
{
    return Motor::Meta::ClassID< T >::klass();
}

#endif
