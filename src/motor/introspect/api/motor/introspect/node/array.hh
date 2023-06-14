/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_ARRAY_HH
#define MOTOR_INTROSPECT_NODE_ARRAY_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Array : public Node
{
private:
    const minitl::vector< ref< Node > > m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    bool           doResolve(DbContext & context) override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit Array(minitl::vector< ref< Node > > value);
    ~Array() override;
};

}}}  // namespace Motor::Meta::AST

#endif
