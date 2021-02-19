/* BugEngine <bugengine.devel@gmail.com>
   see LICENSE for detail */

#ifndef BE_RTTI_AST_NODE_FLOAT4_HH_
#define BE_RTTI_AST_NODE_FLOAT4_HH_
/**************************************************************************************************/
#include <bugengine/rtti-ast/stdafx.h>
#include <bugengine/kernel/simd.hh>
#include <bugengine/rtti-ast/node/node.hh>

namespace BugEngine { namespace RTTI { namespace AST {

class be_api(RTTI_AST) Float4 : public Node
{
private:
    const float4 m_value;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    Float4(float4 value);
    ~Float4();
};

}}}  // namespace BugEngine::RTTI::AST

/**************************************************************************************************/
#endif
