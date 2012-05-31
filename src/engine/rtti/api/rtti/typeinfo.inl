/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_RTTI_TYPEINFO_INL_
#define BE_RTTI_TYPEINFO_INL_
/*****************************************************************************/
#include    <rtti/typeinfo.hh>
#include    <rtti/classinfo.script.hh>


namespace BugEngine { namespace RTTI
{

static inline bool operator==(Type t1, Type t2)
{
    return t1.metaclass == t2.metaclass && t1.indirection == t2.indirection && t1.access == t2.access && t1.constness == t2.constness;
}
static inline bool operator<=(Type t1, Type t2)
{
    return     (t1.indirection <= t2.indirection)
            && t1.access <= t2.access
            && t2.metaclass->isA(t1.metaclass);
}

}


template< typename T >
struct be_typeid< minitl::array<T> >
{
    static inline raw<const RTTI::Class> klass()
    {
        static RTTI::Class ci = {
            "array", {0}, 0, 0, {0}, {0}, {0}, {0}, {0}, {0}, 0, 0
        };
        raw<const RTTI::Class> c = { &ci };
        return c;
    }
    static inline RTTI::Type  type()  { return RTTI::Type::makeType(klass(), RTTI::Type::Value, RTTI::Type::Mutable, RTTI::Type::Mutable); }
};


}

/*****************************************************************************/
#endif
