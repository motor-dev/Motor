/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_NODE_ARRAY_HH_
#define MOTOR_INTROSPECT_NODE_ARRAY_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Array : public Node
{
private:
    const minitl::vector< ref< Node > > m_value;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual bool           doResolve(DbContext & context) override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Array(const minitl::vector< ref< Node > >& value);
    ~Array();

    void visitChildren(Node::Visitor & visitor) const;
};

}}}  // namespace Motor::Meta::AST

/**************************************************************************************************/
#endif
