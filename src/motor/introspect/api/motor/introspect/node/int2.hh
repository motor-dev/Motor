/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_NODE_INT2_HH_
#define MOTOR_INTROSPECT_NODE_INT2_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/kernel/simd.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Int2 : public Node
{
private:
    const bigint2 m_value;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Int2(bigint2 value);
    ~Int2();
};

}}}  // namespace Motor::Meta::AST

/**************************************************************************************************/
#endif
