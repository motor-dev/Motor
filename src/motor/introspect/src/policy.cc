/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/policy.meta.hh>

#include <motor/introspect/introspectionhint.meta.hh>
#include <motor/introspect/node/object.hh>

namespace Motor { namespace Meta { namespace AST {

Policy::~Policy() = default;

ref< IntrospectionHint > Policy::verify(Meta::AST::DbContext&                  context,
                                        const weak< const Meta::AST::Object >& object,
                                        raw< const Method > method, const CallInfo& callInfo,
                                        u32 argumentThis) const
{
    motor_forceuse(context);
    motor_forceuse(object);
    return ref< IntrospectionHint >::create(Arena::meta(), object, method, callInfo, argumentThis);
}

}}}  // namespace Motor::Meta::AST
