/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/kernel/simd.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Float2 : public Node
{
private:
    const knl::float2 m_value;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Float2(knl::float2 value);
    ~Float2();
};

}}}  // namespace Motor::Meta::AST
