/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/policy.script.hh>

#include <motor/introspect/introspectionhint.hh>
#include <motor/introspect/node/object.hh>

namespace Motor { namespace Meta { namespace AST {

Policy::~Policy()
{
}

ref< IntrospectionHint > Policy::verify(Meta::AST::DbContext&           context,
                                        weak< const Meta::AST::Object > object,
                                        const CallInfo& callInfo, u32 argumentThis) const
{
    motor_forceuse(context);
    motor_forceuse(object);
    return ref< IntrospectionHint >::create(Arena::meta(), object, callInfo, argumentThis);
}

}}}  // namespace Motor::Meta::AST
