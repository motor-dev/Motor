/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_PROPERTY_HH
#define MOTOR_INTROSPECT_NODE_PROPERTY_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/introspect/node/object.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Property : public Node
{
private:
    const weak< const Object > m_owner;
    const inamespace           m_propertyName;
    Meta::Type                 m_type;

protected:
    raw< const Meta::Method > getCall(DbContext & context) const override;
    ConversionCost            distance(const Type& type) const override;
    bool                      doResolve(DbContext & context) override;
    void                      doEval(const Type& expectedType, Value& result) const override;
    void                      doVisit(Node::Visitor & visitor) const override;

public:
    Property(const weak< const Object >& owner, inamespace propertyName);
    ~Property() override;
};

}}}  // namespace Motor::Meta::AST

#endif
