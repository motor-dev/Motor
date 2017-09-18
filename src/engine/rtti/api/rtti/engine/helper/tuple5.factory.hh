/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_RTTI_ENGINE_HELPER_TUPLE5_HH_
#define BE_RTTI_ENGINE_HELPER_TUPLE5_HH_
/**************************************************************************************************/
#include    <rtti/stdafx.h>
#include    <rtti/typeinfo.hh>
#include    <rtti/classinfo.script.hh>
#include    <rtti/engine/methodinfo.script.hh>
#include    <rtti/engine/objectinfo.script.hh>
#include    <rtti/engine/propertyinfo.script.hh>
#include    <rtti/engine/helper/get.hh>
#include    <rtti/engine/helper/method.hh>
#include    <minitl/tuple.hh>

namespace BugEngine
{

template< typename T1, typename T2, typename T3, typename T4, typename T5 >
struct be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >
{
    static RTTI::Value make_tuple(RTTI::Value* v, u32 count);
    static RTTI::Value make_default_tuple(RTTI::Value* v, u32 count);
    static const RTTI::Type first_type;
    static const RTTI::Type second_type;
    static const RTTI::Type third_type;
    static const RTTI::Type fourth_type;
    static const RTTI::Type fifth_type;
    static inline raw<RTTI::Class> preklass();
    static inline istring name();
    static inline raw<const RTTI::Class> klass();
    static inline RTTI::Type  type();
private:
    static raw<const RTTI::Class> initialisation;
    static raw<const RTTI::Class> registerProperties();
};


template< typename T1, typename T2, typename T3, typename T4, typename T5 >
be_section(rtti_text_trampoline)
RTTI::Value be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::make_tuple(RTTI::Value* v,
                                                                       u32 count)
{
    be_assert(count == 5, "expected 5 parameters; received %d" | count);
    T1* t1 = static_cast<T1*>(malloca(sizeof(T1)));
    T2* t2 = static_cast<T2*>(malloca(sizeof(T2)));
    T3* t3 = static_cast<T3*>(malloca(sizeof(T3)));
    T4* t4 = static_cast<T4*>(malloca(sizeof(T4)));
    T5* t5 = static_cast<T5*>(malloca(sizeof(T5)));
    new (t1) T1(v[0].as<T1>());
    new (t2) T2(v[1].as<T2>());
    new (t3) T3(v[2].as<T3>());
    new (t4) T4(v[3].as<T4>());
    new (t5) T5(v[4].as<T5>());
    minitl::tuple<T1, T2, T3, T4, T5> result(*t1, *t2, *t3, *t4, *t5);
    t5->~T5();
    t4->~T4();
    t3->~T3();
    t2->~T2();
    t1->~T1();
    freea(t5);
    freea(t4);
    freea(t3);
    freea(t2);
    freea(t1);
    return RTTI::Value(result);
}

template< typename T1, typename T2, typename T3, typename T4, typename T5 >
be_section(rtti_text_trampoline)
RTTI::Value be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::make_default_tuple(RTTI::Value* v,
                                                                               u32 count)
{
    be_assert(count == 0, "expected no parameter; received %d" | count);
    be_forceuse(v);
    be_forceuse(count);
    return RTTI::Value(minitl::tuple<T1, T2, T3, T4, T5>());
}

template< typename T1, typename T2, typename T3, typename T4, typename T5 >
raw<const RTTI::Class> be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::initialisation =
            be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::klass();


template< typename T1, typename T2, typename T3, typename T4, typename T5 >
be_section(rtti_text_cls)
raw<RTTI::Class> be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::preklass()
{
    be_section(rtti_cls)
    static RTTI::Class cls = {
        be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::name(),
        u32(sizeof(minitl::tuple<T1, T2, T3, T4, T5>)),
        0,
        RTTI::ClassType_Struct,
        {be_game_Namespace().m_ptr},
        {be_typeid< void >::preklass().m_ptr},
        {0},
        {&RTTI::staticarray<const RTTI::Tag>::s_null},
        {&RTTI::staticarray<const RTTI::Property>::s_null},
        {&RTTI::staticarray<const RTTI::Method>::s_null},
        {0},
        {0},
        &RTTI::wrapCopy< minitl::tuple<T1, T2, T3, T4, T5> >,
        &RTTI::wrapDestroy< minitl::tuple<T1, T2, T3, T4, T5> >};
    raw< RTTI::Class > result = { &cls };
    return result;
}

template< typename T1, typename T2, typename T3, typename T4, typename T5 >
const RTTI::Type be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::first_type = be_typeid<T1>::type();
template< typename T1, typename T2, typename T3, typename T4, typename T5 >
const RTTI::Type be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::second_type = be_typeid<T2>::type();
template< typename T1, typename T2, typename T3, typename T4, typename T5 >
const RTTI::Type be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::third_type = be_typeid<T3>::type();
template< typename T1, typename T2, typename T3, typename T4, typename T5 >
const RTTI::Type be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::fourth_type = be_typeid<T4>::type();
template< typename T1, typename T2, typename T3, typename T4, typename T5 >
const RTTI::Type be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::fifth_type = be_typeid<T5>::type();


template< typename T1, typename T2, typename T3, typename T4, typename T5 >
be_section(rtti_text_cls_props)
raw<const RTTI::Class> be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::registerProperties()
{
    raw< RTTI::Class > result = preklass();
    be_section(rtti_method)
        static RTTI::staticarray_n< 5, const RTTI::Method::Parameter > s_tuple_0_params = {
        5,
        {
            { {&RTTI::staticarray<const RTTI::Tag>::s_null}, istring("first"), be_typeid< T1 >::type() },
            { {&RTTI::staticarray<const RTTI::Tag>::s_null}, istring("second"), be_typeid< T2 >::type() },
            { {&RTTI::staticarray<const RTTI::Tag>::s_null}, istring("third"), be_typeid< T3 >::type() },
            { {&RTTI::staticarray<const RTTI::Tag>::s_null}, istring("fourth"), be_typeid< T4 >::type() },
            { {&RTTI::staticarray<const RTTI::Tag>::s_null}, istring("fifth"), be_typeid< T5 >::type() }
        }
    };
    be_section(rtti_method)
        static RTTI::staticarray_n< 2, const RTTI::Method::Overload > s_method_tuple_overloads = {
        {2},
        {
            {
                {&RTTI::staticarray<const RTTI::Tag>::s_null},
                { &s_tuple_0_params.array },
                be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type(),
                false,
                &make_tuple
            },
            {
                {&RTTI::staticarray<const RTTI::Tag>::s_null},
                {&RTTI::staticarray<const RTTI::Method::Parameter>::s_null},
                be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type(),
                false,
                &make_default_tuple
            }
        }
    };
    be_section(rtti_method)
        static RTTI::staticarray_n< 1, const RTTI::Method > s_methods = {
        {1},
        {
            {
                istring("tuple"),
                { &s_method_tuple_overloads.array },
                { &s_methods.elements[0] }
            }
        }
    };
    result->methods.set(&s_methods.array);
    be_section(rtti_prop)
        static RTTI::staticarray_n< 5, const RTTI::Property > s_properties = {
        {5},
        {
            {
                {&RTTI::staticarray<const RTTI::Tag>::s_null},
                istring("fifth"),
                be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type(),
                be_typeid< T5  >::type(),
                &RTTI::PropertyHelper< T4 , minitl::tuple<T1, T2, T3, T4, T5>, &minitl::tuple<T1, T2, T3, T4, T5>::fourth >::get
            },
            {
                {&RTTI::staticarray<const RTTI::Tag>::s_null},
                istring("fourth"),
                be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type(),
                be_typeid< T4  >::type(),
                &RTTI::PropertyHelper< T4 , minitl::tuple<T1, T2, T3, T4, T5>, &minitl::tuple<T1, T2, T3, T4, T5>::fourth >::get
            },
            {
                {&RTTI::staticarray<const RTTI::Tag>::s_null},
                istring("third"),
                be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type(),
                be_typeid< T3  >::type(),
                &RTTI::PropertyHelper< T3 , minitl::tuple<T1, T2, T3, T4, T5>, &minitl::tuple<T1, T2, T3, T4, T5>::third >::get
            },
            {
                {&RTTI::staticarray<const RTTI::Tag>::s_null},
                istring("second"),
                be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type(),
                be_typeid< T2  >::type(),
                &RTTI::PropertyHelper< T2 , minitl::tuple<T1, T2, T3, T4, T5>, &minitl::tuple<T1, T2, T3, T4, T5>::second >::get
            },
            {
                {&RTTI::staticarray<const RTTI::Tag>::s_null},
                istring("first"),
                be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type(),
                be_typeid< T1  >::type(),
                &RTTI::PropertyHelper< T1 , minitl::tuple<T1, T2, T3, T4, T5>, &minitl::tuple<T1, T2, T3, T4, T5>::first >::get
            }
        }
    };
    result->properties.set(&s_properties.array);
    return result;
}

template< typename T1, typename T2, typename T3, typename T4, typename T5 >
istring be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::name()
{
    static istring s_name(minitl::format<512u>("tuple<%s,%s,%s,%s,%s>")
                        | be_typeid<T1>::name()
                        | be_typeid<T2>::name()
                        | be_typeid<T3>::name()
                        | be_typeid<T4>::name()
                        | be_typeid<T5>::name());
    return s_name;
}

template< typename T1, typename T2, typename T3, typename T4, typename T5 >
raw<const RTTI::Class> be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::klass()
{
    static raw<const RTTI::Class> result = registerProperties();
    return result;
}

template< typename T1, typename T2, typename T3, typename T4, typename T5 >
RTTI::Type be_typeid< minitl::tuple<T1, T2, T3, T4, T5> >::type()
{
    return RTTI::Type::makeType(klass(), RTTI::Type::Value,
                                RTTI::Type::Mutable, RTTI::Type::Mutable);
}

}

/**************************************************************************************************/
#endif
