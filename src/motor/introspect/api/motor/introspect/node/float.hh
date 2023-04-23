/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Float : public Node
{
private:
    const float m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit Float(float value);
    ~Float() override;
};

}}}  // namespace Motor::Meta::AST
