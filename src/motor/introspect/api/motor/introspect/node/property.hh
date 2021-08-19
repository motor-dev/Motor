/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_NODE_PROPERTY_HH_
#define MOTOR_INTROSPECT_NODE_PROPERTY_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/introspect/node/object.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Property : public Node
{
private:
    const ref< const Object > m_owner;
    const inamespace          m_propertyName;
    Meta::Type                m_type;

protected:
    virtual minitl::tuple< raw< const Meta::Method >, bool > getCall(DbContext & context)
        const override;
    virtual ConversionCost distance(const Type& type) const override;
    virtual bool           doResolve(DbContext & context) override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Property(ref< const Object > owner, const inamespace& propertyName);
    ~Property();
};

}}}  // namespace Motor::Meta::AST

/**************************************************************************************************/
#endif
