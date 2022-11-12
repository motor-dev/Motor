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
    virtual ConversionCost distance(const Type& type) const override;
    virtual bool           doResolve(DbContext & context) override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Parameter(const istring name, ref< Node > value);
    ~Parameter();

    const istring name() const
    {
        return m_name;
    }
};

}}}  // namespace Motor::Meta::AST
