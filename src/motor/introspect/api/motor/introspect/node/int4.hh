/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/kernel/simd.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Int4 : public Node
{
private:
    const knl::bigint4 m_value;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Int4(knl::bigint4 value);
    ~Int4();
};

}}}  // namespace Motor::Meta::AST
