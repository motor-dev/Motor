/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_INTEGER_HH
#define MOTOR_INTROSPECT_NODE_INTEGER_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Integer : public Node
{
private:
    const i64 m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit Integer(i64 value);
    ~Integer() override;
};

}}}  // namespace Motor::Meta::AST

#endif
