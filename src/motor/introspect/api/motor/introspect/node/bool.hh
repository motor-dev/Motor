/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_BOOL_HH
#define MOTOR_INTROSPECT_NODE_BOOL_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Bool : public Node
{
private:
    const bool m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit Bool(bool value);
    ~Bool() override;
};

}}}  // namespace Motor::Meta::AST

#endif
