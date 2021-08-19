/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_NODE_STRING_HH_
#define MOTOR_INTROSPECT_NODE_STRING_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) String : public Node
{
private:
    const char* m_value;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    String(const char* value);
    ~String();
};

}}}  // namespace Motor::Meta::AST

/**************************************************************************************************/
#endif
