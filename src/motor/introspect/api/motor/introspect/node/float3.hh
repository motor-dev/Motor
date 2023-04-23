/* Motor <motor.devel@gmail.com>m_logHandlerGtk
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/kernel/simd.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Float3 : public Node
{
private:
    const knl::float3 m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit Float3(knl::float3 value);
    ~Float3() override;
};

}}}  // namespace Motor::Meta::AST
