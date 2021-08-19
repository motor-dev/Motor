/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_NODE_BOOL_HH_
#define MOTOR_INTROSPECT_NODE_BOOL_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Bool : public Node
{
private:
    const bool m_value;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Bool(bool value);
    ~Bool();
};

}}}  // namespace Motor::Meta::AST

/**************************************************************************************************/
#endif
