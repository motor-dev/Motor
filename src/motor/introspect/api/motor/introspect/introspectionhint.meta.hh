/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_INTROSPECTIONHINT_META_HH_
#define MOTOR_INTROSPECT_INTROSPECTIONHINT_META_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>

#include <motor/introspect/node/node.hh>
#include <motor/meta/engine/call.hh>

namespace Motor { namespace Meta { namespace AST {

class Object;

class motor_api(INTROSPECT) IntrospectionHint : public minitl::refcountable
{
public:
    typedef Meta::ArgInfo< weak< const Node > > ArgInfo;

protected:
    weak< const Object > m_owner;
    raw< const Method >  m_method;
    CallInfo             m_callInfo;
    u32                  m_argumentThis;

public:
    IntrospectionHint(weak< const Object > owner, raw< const Method > method,
                      const CallInfo& callInfo, u32 argumentThis);
    virtual ~IntrospectionHint();

    virtual ConversionCost calculateConversion(const Type& targetType) const;
    virtual Type           getType() const;
    virtual bool           getPropertyType(DbContext & context, const istring propertyName,
                                           Type& propertyType) const;
    virtual Value          call(const ArgInfo arguments[], u32 argumentCount) const;
    virtual minitl::tuple< minitl::raw< const Method >, bool > getCall(DbContext & context) const;
};

}}}  // namespace Motor::Meta::AST

#include <motor/introspect/introspectionhint.inl>

/**************************************************************************************************/
#endif
