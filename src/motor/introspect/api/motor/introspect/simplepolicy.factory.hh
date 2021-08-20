/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_SIMPLEPOLICY_FACTORY_HH_
#define MOTOR_INTROSPECT_SIMPLEPOLICY_FACTORY_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/introspect/policy.meta.hh>

#include <motor/introspect/node/object.hh>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

namespace AST {

template < typename INTROSPECTION_HINT >
struct SimplePolicy : public Policy
{
public:
    virtual ref< IntrospectionHint > verify(Meta::AST::DbContext&           context,
                                            weak< const Meta::AST::Object > object,
                                            const CallInfo& callInfo, u32 argumentThis) const
    {
        motor_forceuse(context);
        return ref< INTROSPECTION_HINT >::create(Arena::meta(), object, callInfo, argumentThis);
    }
};

}  // namespace AST

template < typename INTROSPECTION_HINT >
struct ClassID< AST::SimplePolicy< INTROSPECTION_HINT > >
{
    static MOTOR_EXPORT raw< const Meta::Class > klass()
    {
        static const Meta::Class s_class
            = {istring("SimplePolicy"),
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
               {0},
               &wrap< AST::SimplePolicy< INTROSPECTION_HINT > >::copy,
               &wrap< AST::SimplePolicy< INTROSPECTION_HINT > >::destroy};
        raw< const Meta::Class > result = {&s_class};
        return result;
    }
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
