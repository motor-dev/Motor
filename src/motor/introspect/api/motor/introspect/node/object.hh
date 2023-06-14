/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_OBJECT_HH
#define MOTOR_INTROSPECT_NODE_OBJECT_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

#include <motor/introspect/introspectionhint.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>

namespace Motor { namespace Meta { namespace AST {

class Reference;
class Parameter;

class motor_api(INTROSPECT) Object : public Node
{
private:
    const ref< Reference >                       m_className;
    const minitl::vector< ref< Parameter > >     m_parameters;
    minitl::vector< IntrospectionHint::ArgInfo > m_arguments;
    ref< IntrospectionHint >                     m_introspectionHint;

private:
    bool resolveInternal(DbContext & context);

protected:
    minitl::tuple< raw< const Meta::Method >, bool > getCall(DbContext & context) const override;
    ConversionCost                                   distance(const Type& type) const override;
    bool                                             doResolve(DbContext & context) override;
    ref< Node > getProperty(DbContext & context, const inamespace& propertyName) const override;
    void        doEval(const Type& expectedType, Value& result) const override;
    void        doVisit(Node::Visitor & visitor) const override;

public:
    Object(const ref< Reference >& className, minitl::vector< ref< Parameter > > parameters);
    ~Object() override;

    Type getType() const;
    bool getPropertyValue(Value & value, istring propertyName, Value & result) const;
    bool getPropertyType(DbContext & context, istring propertyName, Type & propertyType) const;

    weak< const Parameter > getParameter(istring name) const;
};

}}}  // namespace Motor::Meta::AST

#endif
