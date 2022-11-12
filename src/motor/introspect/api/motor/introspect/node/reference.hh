/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class Namespace;

class motor_api(INTROSPECT) Reference : public Node
{
    friend class Object;

private:
    const inamespace  m_referenceName;
    ref< const Node > m_node;
    Meta::Value       m_value;

protected:
    virtual minitl::tuple< raw< const Meta::Method >, bool > getCall(DbContext & context)
        const override;
    virtual ConversionCost distance(const Type& type) const override;
    virtual bool           doResolve(DbContext & context) override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Reference(const inamespace& name);
    ~Reference();

    const inamespace& name() const
    {
        return m_referenceName;
    }
};

}}}  // namespace Motor::Meta::AST
