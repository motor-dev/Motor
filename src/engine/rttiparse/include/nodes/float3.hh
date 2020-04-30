/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_RTTIPARSE_NODES_FLOAT3_HH_
#define BE_RTTIPARSE_NODES_FLOAT3_HH_
/**************************************************************************************************/
#include <bugengine/rttiparse/stdafx.h>
#include <bugengine/kernel/simd.hh>
#include <bugengine/rttiparse/valueparse.hh>

namespace BugEngine { namespace RTTI { namespace Parser {

class Float3 : public Node
{
private:
    const float3 m_value;

protected:
    virtual bool isCompatible(const Type& expectedType) const override;
    virtual void doEval(const Type& expectedType, Value& result) const override;

public:
    Float3(const ParseLocation& location, float3 value);
    ~Float3();
};

}}}  // namespace BugEngine::RTTI::Parser

/**************************************************************************************************/
#endif
