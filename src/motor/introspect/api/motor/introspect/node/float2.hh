/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_FLOAT2_HH
#define MOTOR_INTROSPECT_NODE_FLOAT2_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/kernel/simd.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Float2 : public Node
{
private:
    const knl::float2 m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit Float2(knl::float2 value);
    ~Float2() override;
};

}}}  // namespace Motor::Meta::AST

#endif
