/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_PACKAGEBUILDER_NODES_OVERLOADMATCH_HH_
#define BE_PACKAGEBUILDER_NODES_OVERLOADMATCH_HH_
/*****************************************************************************/

namespace BugEngine { namespace PackageBuilder { namespace Nodes
{

class Parameter;

struct OverloadMatch
{
public:
    typedef RTTI::MethodInfo::OverloadInfo::ParamInfo ParamInfo;
    struct ParameterMatch
    {
        weak<const Parameter>   parameter;
        raw<const ParamInfo>    match;
    };
private:
    minitl::vector<ParameterMatch>  m_params;
    u32                             m_score;
public:
    OverloadMatch(raw<const RTTI::MethodInfo::OverloadInfo> overload);
    void addParameter(weak<const Parameter> param);
    bool operator<(const OverloadMatch& other) const;
};

}}}

/*****************************************************************************/
#endif