/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_PACKAGE_NODES_OVERLOADMATCH_HH_
#define BE_PACKAGE_NODES_OVERLOADMATCH_HH_
/**************************************************************************************************/
#include <bugengine/plugin.scripting.package/stdafx.h>
#include <bugengine/rtti/classinfo.script.hh>
#include <bugengine/rtti/engine/call.hh>
#include <bugengine/rtti/engine/methodinfo.script.hh>

namespace BugEngine { namespace PackageBuilder { namespace Nodes {

class Parameter;
class Object;

struct OverloadMatch
{
    friend class Object;

public:
    typedef RTTI::ArgInfo< ref< const Parameter > > ArgInfo;

private:
    minitl::vector< ArgInfo > m_args;
    minitl::vector< u32 >     m_indices;
    RTTI::CallInfo            m_callInfo;

public:
    OverloadMatch(raw< const RTTI::Method::Overload > overload);
    void        update(const minitl::vector< ref< const Parameter > >& parameters);
    RTTI::Value create(istring name) const;

    inline bool operator<(const OverloadMatch& other) const
    {
        return m_callInfo.conversion < other.m_callInfo.conversion;
    }
};

}}}  // namespace BugEngine::PackageBuilder::Nodes

/**************************************************************************************************/
#endif