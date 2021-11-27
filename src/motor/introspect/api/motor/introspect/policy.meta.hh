/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_POLICY_META_HH_
#define MOTOR_INTROSPECT_POLICY_META_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/introspectionhint.hh>

namespace Motor { namespace Meta {

struct CallInfo;

namespace AST {

class Object;

struct motor_api(INTROSPECT) Policy
{
public:
    virtual ~Policy();
    virtual ref< IntrospectionHint > verify(
        Meta::AST::DbContext & context, weak< const Meta::AST::Object > object,
        raw< const Method > method, const CallInfo& callInfo, u32 argumentThis) const;
};

}  // namespace AST
}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
