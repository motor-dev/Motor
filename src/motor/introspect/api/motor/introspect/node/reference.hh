/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_REFERENCE_HH
#define MOTOR_INTROSPECT_NODE_REFERENCE_HH

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
    raw< const Meta::Method > getCall(DbContext & context) const override;
    ConversionCost            distance(const Type& type) const override;
    bool                      doResolve(DbContext & context) override;
    void                      doEval(const Type& expectedType, Value& result) const override;
    void                      doVisit(Node::Visitor & visitor) const override;

public:
    explicit Reference(const inamespace& name);
    ~Reference() override;

    const inamespace& name() const
    {
        return m_referenceName;
    }
};

}}}  // namespace Motor::Meta::AST

#endif
