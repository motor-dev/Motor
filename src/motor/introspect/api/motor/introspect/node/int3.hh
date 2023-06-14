/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_INT3_HH
#define MOTOR_INTROSPECT_NODE_INT3_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/kernel/simd.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Int3 : public Node
{
private:
    const knl::bigint3 m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit Int3(knl::bigint3 value);
    ~Int3() override;
};

}}}  // namespace Motor::Meta::AST

#endif
