/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_SIMPLEPOLICY_FACTORY_HH
#define MOTOR_INTROSPECT_SIMPLEPOLICY_FACTORY_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/policy.meta.hh>

#include <motor/introspect/node/object.hh>
#include <motor/meta/class.meta.hh>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

namespace AST {

template < typename INTROSPECTION_HINT >
struct SimplePolicy : public Policy
{
public:
    ref< IntrospectionHint > verify(Meta::AST::DbContext&           context,
                                    weak< const Meta::AST::Object > object,
                                    raw< const Method > method, const CallInfo& callInfo,
                                    u32 argumentThis) const override
    {
        motor_forceuse(context);
        return ref< INTROSPECTION_HINT >::create(Arena::meta(), object, method, callInfo,
                                                 argumentThis);
    }
};

}  // namespace AST

template < typename INTROSPECTION_HINT >
struct ClassID< AST::SimplePolicy< INTROSPECTION_HINT > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class
            = {name(),
               u32(sizeof(AST::SimplePolicy< INTROSPECTION_HINT >)),
               0,
               Meta::ClassType_Object,
               {0},
               {motor_class< AST::Policy >().m_ptr},
               {0},
               {0},
               {0, 0},
               {0, 0},
               {0},
               Meta::OperatorTable::s_emptyTable,
               &wrap< AST::SimplePolicy< INTROSPECTION_HINT > >::copy,
               &wrap< AST::SimplePolicy< INTROSPECTION_HINT > >::destroy};
        raw< const Meta::Class > result = {&s_class};
        return result;
    }
    MOTOR_EXPORT static istring name()
    {
        static const istring s_name(minitl::format< 4096u >(FMT("SimplePolicy<{0}>"), TypeID< INTROSPECTION_HINT >::name());
        return s_name;
    }
};

}}  // namespace Motor::Meta

#endif
