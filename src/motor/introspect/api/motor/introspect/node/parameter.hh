/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Parameter : public Node
{
private:
    const istring m_name;
    ref< Node >   m_value;

protected:
    ConversionCost distance(const Type& type) const override;
    bool           doResolve(DbContext & context) override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    Parameter(istring name, const ref< Node >& value);
    ~Parameter() override;

    istring name() const
    {
        return m_name;
    }
};

}}}  // namespace Motor::Meta::AST
